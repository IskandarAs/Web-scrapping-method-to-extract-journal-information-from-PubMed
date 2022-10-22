import warnings
from bs4 import BeautifulSoup
import requests
import urllib.request, urllib.parse, urllib.error
import re
import json
import calendar
import numpy as np
import pandas as pd
import time
from sys import exit

warnings.filterwarnings("ignore")

# ===== CODE FOR PUBMED =====
print("Input is from: PubMed.\n")    
url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=NUM&sort=relevance&term=KEYWORD"
keyword = str(input('Please enter the keyword:'))
num = int(input('Please enter the number of results:'))
url = url.replace('NUM', str(num))
url = url.replace('KEYWORD', keyword)

webpage = urllib.request.urlopen(url).read()
dict_page =json.loads(webpage)
idlist = dict_page["esearchresult"]["idlist"]

def strip_brackets(s): 
    no_bracktes = "" 
    dont_want = ['[',']']
    for char in s: 
        if char not in dont_want:
            no_bracktes += char
    return no_bracktes 

# EXTRACTING INFORMATION
def get_bibliography(soup):  
    article = soup.find("article")
    journal = soup.find('journal')


    authorlist = article.find('authorlist')

    authors = ""
    if authorlist:
        for i in range(len(authorlist.find_all('lastname'))):
            initial = authorlist.find_all('initials')[i].text
            authors+= initial
            authors+= '. '
            last_name = authorlist.find_all('lastname')[i].text
            authors+= last_name
            if i == len(authorlist.find_all('lastname'))-2:
                authors += ' and '
            elif i != len(authorlist.find_all('lastname'))-1:
                authors += ', '
        authors += ", "

    ArticleTitle = ''
    if article.find('articletitle'):
            ArticleTitle = '"'
            title_str = article.find('articletitle').text
            title_str = strip_brackets(title_str)
            ArticleTitle += title_str
            if ArticleTitle[-1] == '.':
                ArticleTitle += '", '
            else:
                ArticleTitle += '," '

    journal_title = ''
    if journal.find('title'):
        journal_title = journal.find('title').text
        journal_title += ' '

    JournalIssue = journal.find('journalissue')
    date = JournalIssue.find('year').text

    abstract = ''
    if article.find('abstracttext'):
        abstract = article.find('abstracttext').text

    links = soup.find('articleid').text
    link_url_clean = "https://pubmed.ncbi.nlm.nih.gov/"+str(links)  


    authorlist = soup.find('keywordlist')
    key = ""
    if authorlist:
        for i in range(len(authorlist.find_all('keyword'))):
            last_name = authorlist.find_all('keyword')[i].text
            key+= last_name
            if i == len(authorlist.find_all('keyword'))-2:
                key += ' and '
            elif i != len(authorlist.find_all('keyword'))-1:
                key += ', '
        key += ", "


    result = []
    result.append(authors)
    result.append(ArticleTitle)
    result.append(journal_title)
    result.append(date)
    result.append(abstract)
    result.append(key)
    result.append(link_url_clean)
    return result

articles_list = []        

for link in idlist:
    url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=idlist"
    url = url.replace('idlist', link)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    article = get_bibliography(soup)
    articles_list.append(article)

df = pd.DataFrame(articles_list)
df.columns = ['Authors','Article_Title','Journal_title','Date','Abstract','Keywords','URL']

print("Job finished.")