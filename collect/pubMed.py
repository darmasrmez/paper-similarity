import asyncio
import aiohttp
import requests
import re
import csv
import random
import time
from bs4 import BeautifulSoup

BASE_URL = 'https://pubmed.ncbi.nlm.nih.gov/'

async def extract_info(pmid, session):
    url = f"{BASE_URL}{pmid}/?format=pubmed"
    async with session.get(url) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        
        patterns = {
            'DOI': r"(LID|AID)\s+-\s+(.+)\s+\[doi\]",
            'Title': r"TI  -\s*(.+(?:\n\s{6,}.+)*)",
            'Authors': r"FAU\s+-\s+(.+)\r",
            'Abstract': r"AB  -\s*(.+(?:\n\s{6,}.+)*)",
            'Journal': r"JT  -\s*(.+)\r",
            'Date': r"DP  -\s*(\d{4} \w{3}(?: \d{1,2})?)"
        }
        
        data = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, soup.text)
            data[key] = ', '.join(matches) if key == 'Authors' and matches else (matches[0] if matches else None)
        
        return data if all(data.values()) else None

async def get_pubmed_articles(num_articles):
    articles = set()
    page = 1
    async with aiohttp.ClientSession() as session:
        while len(articles) < num_articles:
            url = f"{BASE_URL}trending/?filter=simsearch1.fha&page={page}"
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            pmids = {tag['href'].split('/')[-2] for tag in soup.find_all('a', class_='docsum-title')}
            
            tasks = [extract_info(pmid, session) for pmid in pmids]
            results = await asyncio.gather(*tasks)
            articles.update(filter(None, results))
            
            page += 1
            time.sleep(random.uniform(1, 2))
            
    return list(articles)[:num_articles]

async def save_articles(articles, filename):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=articles[0].keys())
        writer.writeheader()
        writer.writerows(articles)
    print(f'Los artículos se han guardado en {filename}')

if __name__ == '__main__':
    num_articles = 300
    articles = asyncio.run(get_pubmed_articles(num_articles))
    if articles:
        asyncio.run(save_articles(articles, 'pubmed_raw_corpus.csv'))
