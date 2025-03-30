import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import csv

async def extract_info(page, session, section):
    base_url = 'https://arxiv.org'
    async with session.get(f'{base_url}{page}') as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        date = soup.find('div', class_='dateline').text
        title = soup.find('h1', class_='title mathjax').text
        authors = soup.find_all('div', class_='authors')[0].text
        abstract = soup.find('blockquote', class_='abstract mathjax').text
        doi = soup.find('a', id='arxiv-doi-link').text

        # cleaning data
        date = date.replace('Submitted on ', '').replace('[', '').replace(']', '').replace('\n', '').strip()
        title = title.replace('Title:', '').strip()
        abstract = abstract.replace('Abstract:', '').strip()
        authors = authors.replace('Authors:', '').strip()
        abstract = abstract.replace('\n', '').strip()
        doi = doi.strip()

        return [doi, title, authors, abstract, section, date]

async def get_arxiv_papers(arxiv, csv_writer):
    source = requests.get(arxiv).text
    soup = BeautifulSoup(source, 'html.parser')
    papers = soup.find_all('a', href=True, title='Abstract')
    section = arxiv.split('/')[-2].split('.')[-1]

    async with aiohttp.ClientSession() as session:
        tasks = [extract_info(paper['href'], session, section) for paper in papers]
        list_of_details = await asyncio.gather(*tasks)

        for paper in list_of_details:
            csv_writer.writerow(paper)

if __name__ == '__main__':
    links = ['https://arxiv.org/list/cs.CL/recent', 'https://arxiv.org/list/cs.CL/recent?skip=50&show=50',
             'https://arxiv.org/list/cs.CL/recent?skip=100&show=50', 'https://arxiv.org/list/cs.CV/recent',
             'https://arxiv.org/list/cs.CV/recent?skip=50&show=50', 'https://arxiv.org/list/cs.CV/recent?skip=100&show=50']

    with open('../data/arxiv_raw_corpus.csv', 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter=',')
        csv_writer.writerow(["DOI", "Title", "Authors", "Abstract", "Section", "Date"])

        for link in links:
            asyncio.run(get_arxiv_papers(link, csv_writer))

    print("Archivo arxiv_raw_corpus.csv guardado correctamente.")