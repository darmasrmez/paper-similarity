import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

pubmed_reference = {
    
}

def parse_pubmed_format(content):
    lines = content.split('\n')
    for 
    return [date, title, authors, abstract, doi]

async def extract_info(page, session):
    base_url = 'https://pubmed.ncbi.nlm.nih.gov'
    async with session.get(f'{base_url}{page}?format=pubmed') as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        content = soup.find('pre', class_='article-details').text



async def get_pubmed_papers(pubmed_list):
    source = requests.get(pubmed_list).text
    soup = BeautifulSoup(source, 'html.parser')
    papers = soup.find_all('a', class_='docsum-title', href=True)
    async with aiohttp.ClientSession() as session:
        tasks = [
            extract_info(paper['href'], session)
            for paper in papers
        ]
        list_of_details = await asyncio.gather(*tasks)
        print(list_of_details)
        print(len(list_of_details))

if __name__ == '__main__':
    links = ['https://pubmed.ncbi.nlm.nih.gov/trending/']

    generate_links = lambda x: f'https://pubmed.ncbi.nlm.nih.gov/trending/?page={x}'
    for i in range(2, 11):
        links.append(generate_links(i))

    for link in links:
        get_pubmed_papers(link)