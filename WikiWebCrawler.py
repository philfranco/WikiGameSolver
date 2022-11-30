import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
# from similarityCheck import wordScore

def main():
    # Identify Starting Page
    print('Starting')
    start_article = 'Deer' # "Wilhelmy plate"
    end_article = 'Field Hockey' # "America's Cup"

    current_article = start_article

    # page_text = getText(current_article, end_article)
    # page_links = getLinks(current_article)
    
    # steps, pages_visited = playWikiGame(start_article, end_article)
    # print("It took " + str(steps) + " links to get from " + start_article + " to " + end_article)

    data = recursiveSearch(1, [start_article], {}, end_article)

    # Create Network Graph
    df = pd.DataFrame(data)

    G = nx.from_pandas_edgelist(df, source='source', target='target')

    nx.draw_networkx(G)

    plt.show()

def getLinksFromTextBS(start_article, end_article):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': start_article,
        'format': 'json',
        'prop': 'text',
        'redirects': ''
    }

    filter_sections = ['See also',
                       'References',
                       'External links',
                       'Further reading',
                       'Notes']

    response = requests.get(url, params=params)
    data = response.json()

    raw_html = data['parse']['text']['*']
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Get all the section names
    allSections = soup.find_all(class_='mw-headline')

    sectionNames = []
    for section in allSections:
        sectionNames.append(section.get_text())

    sectionNames = [x for x in sectionNames if x not in filter_sections]

    # Get links from summary section

    # Get all the links from each of the relevant sections
    for thisSection in sectionNames:
        print('==--------' + thisSection + '--------==')
        target = soup.find(class_='mw-headline', id=thisSection.replace(' ', '_'))
        for sib in target.find_all_next():
            # Only look in current section, end if hitting next section
            # print(sib)
            if sib.name == "h2":
                break
            else:
                # Check if href contains internal /wiki/ path
                check1 = 'href' in sib.attrs and \
                '/wiki/' in sib.attrs['href']
                # Check if tag contains class mw-redirect
                check2 = 'class' in sib.attrs and \
                    'mw-redirect' in sib.attrs['class']
                if (check1 or check2) and 'title' in sib.attrs:
                    print(sib.attrs['title'])


def playWikiGame(head, final):
    steps = 0
    pages = [head]
    pages_visited = []
    
    # forces the words to be the same case
    while not str.lower(head) == str.lower(final):
        result_links = getLinks(head)
        # len_target = len(final)
        scores = wordScore(final, result_links)

        # create dataframe
        df_wiki = pd.DataFrame(list(zip(result_links, scores)),
               columns =['target', 'weight'])
        
        # sort dataframe and reorganize index
        df_wiki_org = df_wiki.sort_values(by=['weight'], ascending=False)
        df_wiki_org = df_wiki_org.reset_index(drop=True)
        
        # if the page has already been searched, drop it from the current links
        while df_wiki_org['target'][0] in pages:
            df_wiki_org = df_wiki_org.drop(labels=0, axis=0)
            df_wiki_org = df_wiki_org.reset_index(drop=True)

        head = df_wiki_org['target'][0]
        pages.append(head)
        print(head)
        steps = steps + 1
        pages_visited.append(head)

    return steps, pages_visited

def recursiveSearch(N, page_links, data, end_article):
    print('Search Depth Remaining: {}'.format(N))
    new_data = {}
    new_links = []

    for link in page_links:
        print(link)
        result_links = getLinks(link)
        wiki_data = createWikiGraph(link, result_links)
        new_data.update(wiki_data)
        new_links = new_links + result_links
        if end_article in new_links:
            break

    new_data.update(data)
    if N == 0:
        return new_data
    else:
        return recursiveSearch(N - 1, new_links, new_data, end_article)

def createWikiGraph(source, target):    
    len_target = len(target)
    # scores = wordScore(source, target)
    scores = [1] * len_target
    wikiData = {'source': [source for i in range(len_target)],
                'target': target,
                'weight': scores}

    df_wiki = pd.DataFrame(list(zip( [source for i in range(len_target)], target, scores)),
               columns =['source', 'target', 'weight'])
    
    df_wiki_org = df_wiki.sort_values(by=['weight'], ascending=False)

    return wikiData 

def getText(start_article, end_article):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': start_article,
        'format': 'json',
        'prop': 'text',
        'redirects': ''
    }

    response = requests.get(url, params=params)
    data = response.json()

    raw_html = data['parse']['text']['*']
    soup = BeautifulSoup(raw_html, 'html.parser')
    soup.find_all('p')
    text = ''

    for p in soup.find_all('p'):
        text += p.text

    print(len(word_tokenize(text)))
    print('Number of words: ', len(text))

    return text

def getSections(start_article):
    filter_sections = ['See_also',
                       'References',
                       'External_links',
                       'Further_reading']

    url = 'https://en.wikipedia.org/w/api.php'

    params = {
        'action': 'parse',
        'format': 'json',
        'page': start_article,
        'prop': 'sections',
        'redirects': ''
    }

    response = requests.get(url=url, params=params)
    data = response.json()

    sections = data['parse']['sections']

    # Remove sections in filter list
    sections_filt = [x for x in sections if x['anchor'] not in filter_sections]

    # Get section IDs
    section_ids = [x['index'] for x in sections_filt]

    return section_ids

def getLinks(start_article):
    page_titles = []
    section_ids = getSections(start_article)
    url = 'https://en.wikipedia.org/w/api.php'

    for idx in section_ids:
        params = {
            'action': 'parse',
            'format': 'json',
            'page': start_article,
            'prop': 'links',
            'section': int(idx) - 1,
            'redirects': ''
        }

        response = requests.get(url=url, params=params)
        data = response.json()
        links = data['parse']['links']

        # Remove results that are not in the 'main' namespace
        # More info: https://www.mediawiki.org/wiki/Help:Namespaces
        page_titles = page_titles + [x['*'] for x in links if x['ns'] == 0]

    print('# Links: {}'.format(len(page_titles[:])))
    return page_titles

if __name__ == "__main__":
    main()
