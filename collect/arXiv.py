import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

async def extract_info(page, session):
    base_url = 'https://arxiv.org'
    async with session.get(f'{base_url}{page}') as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        date = soup.find('div', class_='dateline').text
        title = soup.find('h1', class_='title mathjax').text
        authors = soup.find_all('div', class_='authors')[0].text
        abstract = soup.find('blockquote', class_='abstract mathjax').text
        doi = soup.find('a', id='arxiv-doi-link').text
        return [date, title, authors, abstract, doi]


async def get_arxiv_papers(arxiv):
    source = requests.get(arxiv).text
    soup = BeautifulSoup(source, 'html.parser')
    papers = soup.find_all('a', href=True, title='Abstract')
    async with aiohttp.ClientSession() as session:
        tasks = [
            extract_info(paper['href'], session)
            for paper in papers
        ]
        list_of_details = await asyncio.gather(*tasks)
        print(list_of_details)
        print(len(list_of_details))

if __name__ == '__main__':
    links = ['https://arxiv.org/list/cs.CL/recent', 'https://arxiv.org/list/cs.CL/recent?skip=50&show=50', 'https://arxiv.org/list/cs.CL/recent?skip=100&show=50']
    for link in links:
        asyncio.run(get_arxiv_papers(link))