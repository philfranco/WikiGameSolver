import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from similarityCheck import wordScore, coding_test
import time

def main():
    # Identify Starting Page
    print('Starting')

    start_article = 'Amazon River' # "Wilhelmy plate"
    end_article = 'Emotion' # "America's Cup"

    current_article = start_article

    # page_text = getText(current_article, end_article)
    # page_links = getLinks(current_article)
    
    steps_l6, pages_visited_l6, time_l6, win_l6 = playWikiGame(start_article, end_article, 'L6')
    # print("L6: It took " + str(steps_l6) + " links to get from " + start_article + " to " + end_article)
 
    steps_l12, pages_visited_l12, time_l12, win_l12 = playWikiGame(start_article, end_article, 'L12')
    # print("L12: It took " + str(steps_l12) + " links to get from " + start_article + " to " + end_article)

    steps_micro, pages_visited_micro, time_micro, win_micro = playWikiGame(start_article, end_article, 'microsoftNet')
    # print("Microsoft: It took " + str(steps_micro) + " links to get from " + start_article + " to " + end_article)

    steps_bert, pages_visited_bert, time_bert, win_bert = playWikiGame(start_article, end_article, 'bert')
    # print("Bert: It took " + str(steps_bert) + " links to get from " + start_article + " to " + end_article)

    steps_roberta, pages_visited_roberta, time_roberta, win_roberta = playWikiGame(start_article, end_article, 'roberta')
    # print("Roberta: It took " + str(steps_roberta) + " links to get from " + start_article + " to " + end_article)
   
    print("L6:        It took " + str(steps_l6) + " links to get from " + start_article + " to " + end_article +  " in " + time_l6)
    print("L12:       It took " + str(steps_l12) + " links to get from " + start_article + " to " + end_article +  " in " + time_l12)
    print("Microsoft: It took " + str(steps_micro) + " links to get from " + start_article + " to " + end_article +  " in " + time_micro)
    print("Bert:      It took " + str(steps_bert) + " links to get from " + start_article + " to " + end_article +  " in " + time_bert)
    print("Roberta:   It took " + str(steps_roberta) + " links to get from " + start_article + " to " + end_article +  " in " + time_roberta)

    # Find true distances
    tic = time.perf_counter()
    data = recursiveSearch(3, [start_article], {'source': [], 'target': [], 'weight': []}, end_article)
    toc = time.perf_counter()
    time_search = toc-tic

    # Create Network Graph
    df = pd.DataFrame(data)

    pages_visited_search = df.source.unique()
    steps_search = len(df.source.unique())

    steps_true = buildNetwork(df, start_article, end_article)


def buildNetwork(df, start_article, end_article):
    G = nx.from_pandas_edgelist(df, source='source', target='target')

    color_map = []
    size_map = []

    # Shortest path between start and end article
    p = nx.shortest_path(G, source=start_article, target=end_article, method='dijkstra')

    # # Format network plot
    # for node in G:
    #     if node in start_article:
    #         color_map.append('green')
    #         size_map.append(100)
    #     elif node in end_article:
    #         color_map.append('red')
    #         size_map.append(100)
    #     elif node in p:
    #         color_map.append('blue')
    #         size_map.append(100)
    #     else:
    #         color_map.append('beige')
    #         size_map.append(1)
    #
    # nx.draw_spring(G, with_labels=False, node_color=color_map, node_size=size_map)
    # plt.show()

    return p

def getLinksFromTextBS(start_article):
    page_titles = []
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

    if 'error' in data:
        return ''

    raw_html = data['parse']['text']['*']
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Get all the section names
    allSections = soup.find_all(class_='mw-headline')

    sectionNames = []
    for section in allSections:
        sectionNames.append(section.get_text())

    sectionNames = [x for x in sectionNames if x not in filter_sections]

    # Get links from summary section up to the Table of Contents
    target = soup.find(class_='mw-parser-output')
    if target:
        for sib in target.find_all_next():
            # Only look in current section, end if hitting next section
            # print(sib)
            if sib.name == "h2":
                break
            elif 'title' in sib.attrs and 'Edit this' in sib.attrs['title']:
                # Don't include the hrefs to edit the pages
                continue
            else:
                # Check if href contains internal /wiki/ path
                check1 = 'href' in sib.attrs and \
                         '/wiki/' in sib.attrs['href']
                # Check if tag contains class mw-redirect
                check2 = 'class' in sib.attrs and \
                         'mw-redirect' in sib.attrs['class']
                # Not an image class
                check3 = 'class' in sib.attrs and \
                    'image' in sib.attrs['class']

                if (check1 or check2) and not check3 and \
                        'title' in sib.attrs and \
                        ':' not in sib.attrs['title'] and \
                        'wiktionary' not in sib.attrs['title']:
                    page_titles.append(sib.attrs['title'])

    # Get all the links from each of the relevant sections
    for thisSection in sectionNames:
        # print('==--------' + thisSection + '--------==')
        target = soup.find(class_='mw-headline', id=thisSection.replace(' ', '_'))
        if target:
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
                    # Not an image class
                    check3 = 'class' in sib.attrs and \
                             'image' in sib.attrs['class']
                    if (check1 or check2) and not check3 and \
                            'title' in sib.attrs and \
                            ':' not in sib.attrs['title'] and \
                            'wiktionary' not in sib.attrs['title']:
                        page_titles.append(sib.attrs['title'])
    # Unique pages only
    page_titles = list(set(page_titles))
    return page_titles

def playWikiGame(head, final, model):
    steps = 0
    pages = [head]
    pages_visited = []
    win = True

    tic = time.perf_counter()
    
    # forces the words to be the same case
    while not str.lower(head) == str.lower(final):
        result_links = getLinksFromTextBS(head)
        len_target = len(final)

        scores = wordScore(final, result_links, model)

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
        # print(head)
        steps = steps + 1
        pages_visited.append(head)
        toc = time.perf_counter()
        if toc - tic > 120:
            # Break if reach time limit
            win = False
            break

    toc = time.perf_counter()

    print(model + " took " + str(toc - tic) + " seconds to complete")
    print('Game Win: {}'.format(win))
    return steps, pages_visited, str(toc - tic), win

def recursiveSearch(N, page_links, data, end_article):
    print('Search Depth Remaining: {}'.format(N))
    new_data = {'source': [], 'target': [], 'weight': []}
    new_links = []

    for link in page_links:
        # result_links = getLinks(link)
        result_links = getLinksFromTextBS(link)

        # Don't revisit any links
        result_links = [l for l in result_links if l not in page_links]

        if result_links:
            # Save result links into dictionary
            wiki_data = createWikiGraph(link, result_links)

            new_data['source'].extend(wiki_data['source'])
            new_data['target'].extend(wiki_data['target'])
            new_data['weight'].extend(wiki_data['weight'])

            new_links = new_links + result_links
            if end_article in new_links:
                print('======================')
                print('FOUND: ' + end_article)
                print('======================')
                N = 0
                break

    new_data['source'].extend(data['source'])
    new_data['target'].extend(data['target'])
    new_data['weight'].extend(data['weight'])

    if N == 0:
        return new_data
    else:
        return recursiveSearch(N - 1, new_links, new_data, end_article)

def createWikiGraph(source, target):    
    len_target = len(target)

    # NOT SURE WHAT MODEL TO USE
    scores = wordScore(source, target, "L6")

    # scores = [1] * len_target
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
    #coding_test()
    main()