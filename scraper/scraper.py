import requests
from bs4 import BeautifulSoup
import os
import asyncio
import aiohttp

from dotenv import load_dotenv

load_dotenv()
brave_key = os.getenv("BRAVE_KEY")
# print(f"Brave Key: {brave_key}")
import time
import json


MAX_SCRAPED_LEN = 1024



def fetch_urls(response):
    
    urls = []    
    
    results_dict = response.json()
    # Parse the HTML content of the search results page
    soup = BeautifulSoup(response.text, 'html.parser')
    attrs = [f"{val} \n\n" for val in soup.contents]
    for res in results_dict['web']['results']:
        urls.append(res['url'])
    return urls

async def fetch_content(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await async_remove_tags(await response.read())
                return content
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
    return None

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_content(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

def fetch_context(query):

    url = "https://api.search.brave.com/res/v1/web/search"
    api_key = brave_key
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    total_content = []
    
    params = {
        "q": query,
        "count": 4
    }

    response = requests.get(url, headers=headers, params=params)

    
    
    # # Send an HTTP GET request to the search engine
    if response.status_code == 200:
        urls = fetch_urls(response)
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        results = loop.run_until_complete(fetch_all(urls))
    # Process fetched content and summarize
        for content in results:
            if content:
                total_content.append(content[:min(len(content), MAX_SCRAPED_LEN)])

    else:
        print("Failed to fetch real-time data. Status code:", response.status_code)
    
    return total_content

 
# Function to remove tags
async def async_remove_tags(html):
 
    # parse html content
    soup = BeautifulSoup(html, "html.parser")
 
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
 
    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)
 
def remove_tags(html):
 
    # parse html content
    soup = BeautifulSoup(html, "html.parser")
 
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
 
    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)
 


def fetch_images(query):

    url = "https://api.search.brave.com/res/v1/images/search"
    api_key = brave_key

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    titles = query.split(',')
    url_list = []
    for q in titles:
        params = {
            "q": q,
            "count": 10
        }
        print(f"Image Query: {q}")
        response = requests.get(url, headers=headers, params=params)
        try:
            # # Send an HTTP GET request to the search engine
            if response.status_code == 200:
                results_dict = response.json()
                # Parse the HTML content of the search results page
                soup = BeautifulSoup(response.text, 'html.parser')
                attrs = [f"{val} \n\n" for val in soup.contents]
                urls = []
                # print(soup.get_text())
                for res in results_dict['results']:
                    urls.append(res['thumbnail']['src'])

                for url in urls:
                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            url_list.append(url)

                    except:
                        print(f"Invalid url : {url}")
            else:
                print("Failed to fetch real-time data. Status code:", response.status_code)
        except:
            print("Cant retrieve")
        
    print(url_list)
    return url_list


if __name__ == "__main__":
    import time
    query = "Suggest 3 books by Enid Blyton"
    start_ts = time.time()
    total_content = fetch_context(query)
    
    for c in total_content:
        print("="*100)
        print(c)
        print("="*100)
    
    end_ts = time.time()
    print(f"Time taken {end_ts - start_ts} seconds")