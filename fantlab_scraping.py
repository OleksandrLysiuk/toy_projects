import os
import zipfile
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup                
import requests

# get list of .mobi books in my library
dir_list = os.listdir('C:/library')
books = ['a']
for i in dir_list:
    if i[-3:] == 'zip':
        path = 'C:/Library/' + i
        zip = zipfile.ZipFile(path)
        files = zip.namelist()
        for file in files:
            x = re.findall("[A-Za-z. ']+/[A-Za-z]+[A-Za-z. ']+", file)
            if len(x)>0:
                if x[0]!=books[-1]:
                    books.append(x[0])

# scraping fantlab.ru for intereste info about books
fantlab = pd.DataFrame()
for i in np.arange(1, 1100):
    url_author = 'https://fantlab.ru/author' + str(i)
    html_author = requests.get(url_author).content
    soup_author = BeautifulSoup(html_author)
    if not soup_author.find('h1', itemprop="name"):
        print(i, 'no author')
    else:
        name = soup_author.find('h1', itemprop="name").get_text()
        print(i, name)
        if soup_author.find('tbody', id='novel_info'): 
            category = soup_author.find('tbody', id='novel_info')
            rows = fantlab.shape[0]
            for n, novel in enumerate(category.find_all('tr', valign='bottom')):
                i = rows + n
                if '(' in name:
                    fantlab.loc[i, 'author_eng'] = re.findall("\((.*?)\)$", name)[0]
                    fantlab.loc[i, 'author_rus'] = re.findall("^(.*) \(.*", name)[0] 
                else:
                    fantlab.loc[i, 'author_rus'] = name
                fantlab.loc[i, 'story_type'] = 'novel'
                fantlab.loc[i, 'title_rus'] = novel.find('a', title=False).get_text()
                # agray = novel.find('a', class_='agray')
                # fantlab.loc[i, 'title_origin'] = agray.get_text()
                # url_book = agray['href']
                
                if novel.find('a', class_='agray'):
                    agray = novel.find('a', class_='agray')
                    fantlab.loc[i, 'title_origin'] = agray.get_text()
                    url_book = agray['href']
                else:
                    fantlab.loc[i, 'title_origin'] = np.nan
                    url_book = novel.find('a', title=False)['href']
                if novel.find('font'):  
                    fantlab.loc[i, 'book_year'] = novel.find('font').get_text()
                book_cycle = novel.find('a').get('title', '«»')
                try:
                    fantlab.loc[i, 'cycle'] = re.findall("«(.*?)»$", book_cycle)[0]
                except Exception:
                    fantlab.loc[i, 'cycle'] = book_cycle
               
                # fantlab.loc[i, 'annotation'] = novel.find('nobr').find('a').get('title', '')
                # fantlab.loc[i, 'annotation'] = novel.find('td', align='right').find('nobr').find('a').get('title', '')
                
                if novel.find('td', align='right').find('nobr').find('a'): 
                        fantlab.loc[i, 'annotation'] = novel.find('td', align='right').find('nobr').find('a').get('title', '')               
                else:
                    fantlab.loc[i, 'annotation'] = np.nan
                if novel.find('span', id=True):
                    span = novel.find('span', id=True).get_text()
                    fantlab.loc[i, 'number_marks'] = re.findall("\((.*?)\)$", span)[0]
                    fantlab.loc[i, 'mark'] = re.findall("^(.*) \(.*", span)[0]
                if novel.find('font', color='#00A000'):
                    number_of_reviews = novel.find('font', color='#00A000').get_text()
                    fantlab.loc[i, 'number_reviews'] = [int(s) for s in number_of_reviews.split() if s.isdigit()][0] 
                url_book = 'https://fantlab.ru' + url_book
                html_book = requests.get(url_book).content
                soup_book = BeautifulSoup(html_book)
                if soup_book.find('div', id='workclassif'):
                    for b in soup_book.find('div', id='workclassif').find_all('li'):
                        c = b.find_all('a')
                        f = b.find_all('span', class_=True)
                        for a in range(len(c)):
                             y = f[a].get('title', '')
                             fantlab.loc[i, 'description_total_votes'] = y.split(' из ')[1]
                             fantlab.loc[i, c[0].previous_sibling + c[a].get_text()] = y.split(' из ')[0] 
        if soup_author.find('tbody', id='cycle_info'):                  
            category = soup_author.find('tbody', id='cycle_info')
            rows = fantlab.shape[0]
            for n, tr in enumerate(category.find_all('tr', valign='bottom')):
                i = rows + n
                if '(' in name:
                    fantlab.loc[i, 'author_eng'] = re.findall("\((.*?)\)$", name)[0]
                    fantlab.loc[i, 'author_rus'] = re.findall("^(.*) \(.*", name)[0] 
                else:
                    fantlab.loc[i, 'author_rus'] = name
                fantlab.loc[i, 'story_type'] = 'cycle'
                fantlab.loc[i, 'title_rus'] = tr.find('a', title=False).get_text()
                if tr.find('a', class_='agray'):
                    agray = tr.find('a', class_='agray')
                    fantlab.loc[i, 'title_origin'] = agray.get_text()
                    url_book = agray['href']
                else:
                    fantlab.loc[i, 'title_origin'] = np.nan
                    url_book = tr.find('a', title=False)['href']
                # if not tr.find('nobr').find('a'): fantlab.loc[i, 'annotation'] = np.nan
                # if tr.find('nobr').find('a'): fantlab.loc[i, 'annotation'] = tr.find('nobr').find('a').get('title', '')
                if tr.find('td', align='right').find('nobr').find('a'): 
                    fantlab.loc[i, 'annotation'] = tr.find('td', align='right').find('nobr').find('a').get('title', '')               
                else:
                    fantlab.loc[i, 'annotation'] = np.nan
                if tr.find('span', id=True):
                    span = tr.find('span', id=True).get_text()
                    fantlab.loc[i, 'number_marks'] = re.findall("\((.*?)\)$", span)[0]
                    fantlab.loc[i, 'mark'] = re.findall("^(.*) \(.*", span)[0]
                if not tr.find('font', color='#00A000'): number_of_reviews = '0'
                if tr.find('font', color='#00A000'): number_of_reviews = tr.find('font', color='#00A000').get_text()
                fantlab.loc[i, 'number_reviews'] = [int(s) for s in number_of_reviews.split() if s.isdigit()][0]
                url_book = 'https://fantlab.ru' + url_book
                html_book = requests.get(url_book).content
                soup_book = BeautifulSoup(html_book)
                if soup_book.find('div', id='workclassif'):
                    for b in soup_book.find('div', id='workclassif').find_all('li'):
                        c = b.find_all('a')
                        f = b.find_all('span', class_=True)
                        for a in range(len(c)):
                             y = f[a].get('title', '')
                             fantlab.loc[i, 'description_total_votes'] = y.split(' из ')[1]
                             fantlab.loc[i, c[0].previous_sibling + c[a].get_text()] = y.split(' из ')[0]
        if soup_author.find('tbody', id='epic_info'):                 
            category = soup_author.find('tbody', id='epic_info')
            rows = fantlab.shape[0]
            for n, tr in enumerate(category.find_all('tr', valign='bottom')):
                i = rows + n
                if '(' in name:
                    fantlab.loc[i, 'author_eng'] = re.findall("\((.*?)\)$", name)[0]
                    fantlab.loc[i, 'author_rus'] = re.findall("^(.*) \(.*", name)[0] 
                else:
                    fantlab.loc[i, 'author_rus'] = name
                fantlab.loc[i, 'story_type'] = 'epic'
                fantlab.loc[i, 'title_rus'] = tr.find('a', title=False).get_text()
                if tr.find('a', class_='agray'):
                    agray = tr.find('a', class_='agray')
                    fantlab.loc[i, 'title_origin'] = agray.get_text()
                    url_book = agray['href']
                else:
                    fantlab.loc[i, 'title_origin'] = np.nan
                    url_book = tr.find('a', title=False)['href']
                # if tr.find('nobr').find('a'): 
                #     fantlab.loc[i, 'annotation'] = tr.find('nobr').find('a').get('title', '')
                # else:
                #     fantlab.loc[i, 'annotation'] = np.nan
                if tr.find('td', align='right').find('nobr').find('a'): 
                    fantlab.loc[i, 'annotation'] = tr.find('td', align='right').find('nobr').find('a').get('title', '')               
                else:
                    fantlab.loc[i, 'annotation'] = np.nan    
                if tr.find('span', id=True):
                    span = tr.find('span', id=True).get_text()
                    fantlab.loc[i, 'number_marks'] = re.findall("\((.*?)\)$", span)[0]
                    fantlab.loc[i, 'mark'] = re.findall("^(.*) \(.*", span)[0]
                if not tr.find('font', color='#00A000'): number_of_reviews = '0'
                if tr.find('font', color='#00A000'): number_of_reviews = tr.find('font', color='#00A000').get_text()
                fantlab.loc[i, 'number_reviews'] = [int(s) for s in number_of_reviews.split() if s.isdigit()][0]
                url_book = 'https://fantlab.ru' + url_book
                html_book = requests.get(url_book).content
                soup_book = BeautifulSoup(html_book)
                if soup_book.find('div', id='workclassif'):
                    for b in soup_book.find('div', id='workclassif').find_all('li'):
                        c = b.find_all('a')
                        f = b.find_all('span', class_=True)
                        for a in range(len(c)):
                             y = f[a].get('title', '')
                             fantlab.loc[i, 'description_total_votes'] = y.split(' из ')[1]
                             fantlab.loc[i, c[0].previous_sibling + c[a].get_text()] = y.split(' из ')[0]
# save scraping info to disk                             
fantlab.to_csv('C:/datasets/fantlab.csv', index=False)

# matching library and scraping info
fantlab['key'] = fantlab.author_eng + '/' + fantlab.title_origin + ' '
books_df = pd.DataFrame(books, columns = ['library'])
united = books_df.merge(fantlab, how = 'inner', left_on = 'library', right_on = 'key')

#save to disk
united.to_csv('C:/datasets/united.csv', index = False)
