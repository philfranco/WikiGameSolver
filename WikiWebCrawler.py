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
    start_article = 'Cégep du Vieux Montréal' # "Wilhelmy plate"
    end_article = 'Field Hockey' # "America's Cup"

    current_article = start_article

    # page_text = getText(current_article, end_article)
    # page_links = getLinks(current_article)
    
    # steps, pages_visited = playWikiGame(start_article, end_article)
    # print("It took " + str(steps) + " links to get from " + start_article + " to " + end_article)

    data = recursiveSearch(1, [start_article], {})

    # Create Network Graph
    df = pd.DataFrame(data)

    G = nx.from_pandas_edgelist(df, source='source', target='target')

    nx.draw_networkx(G)

    plt.show()

def playWikiGame(head, final):
    steps = 0
    pages = [head]
    pages_visited = []
    
    # forces the words to be the same case
    while not str.lower(head) == str.lower(final):
        result_links = getLinks(head)
        len_target = len(final)
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

def recursiveSearch(N, page_links, data):
    print('Search Depth Remaining: {}'.format(N))
    new_data = {}
    new_links = []

    for link in page_links:
        print(link)
        result_links = getLinks(link)
        wiki_data = createWikiGraph(link, result_links)
        new_data.update(wiki_data)
        new_links = new_links + result_links

    new_data.update(data)

    if N == 0:
        return new_data
    else:
        return recursiveSearch(N - 1, new_links, new_data)

def createWikiGraph(source, target):    
    len_target = len(target)
    scores = wordScore(source, target)
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
                       'External_links']

    section_titles = []

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
    for val in sections:
        section_titles.append(val['anchor'])

    section_titles = [x for x in section_titles if x not in filter_sections]

    return section_titles

def getLinks(start_article):
    section_titles = getSections(start_article)

    url = 'https://en.wikipedia.org/w/api.php'

    # params = {
    #     'action': 'query',
    #     'format': 'json',
    #     'titles': start_article,
    #     'prop': 'links',
    #     'pllimit': 'max',
    #     'redirects': ''
    # }

    params = {
        'action': 'parse',
        'format': 'json',
        'page': start_article,
        'prop': 'links',
        'section' : '|'.join(section_titles),
        'redirects': ''
    }

    response = requests.get(url=url, params=params)
    data = response.json()

    pages = data['query']['pages']
    page = 1
    page_titles = []
    import pdb; pdb.set_trace()
    for key, val in pages.items():
        if 'links' in val:
            for link in val['links']:
                page_titles.append(link['title'])

    while 'continue' in data:
        plcontinue = data['continue']['plcontinue']
        params['plcontinue'] = plcontinue

        response = requests.get(url=url, params=params)
        data = response.json()
        pages = data['query']['pages']

        page += 1

        for key, val in pages.items():
            for link in val['links']:
                page_titles.append(link['title'])


    print('# Links: {}'.format(len(page_titles[:])))
    return page_titles

if __name__ == "__main__":
    main()
