import requests
from bs4 import BeautifulSoup
import re
import os
import openai
from openai import OpenAI
openai.api_key = os.getenv("OAI_KEY")
client = OpenAI()
import json



def openAI_api_call(mode, query, msgs = None):

    if mode == "Summarize":    
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        # response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to cleanup and compress data collected scraped from a website."},
            {"role": "user", "content": query}
        ]
        )
    elif mode == "img_search":
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        # response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to extract book or movie titles from a given answer by another assistant if the answer has titles. Put the extracted titles in a comma separated list"},
            {"role": "user", "content": query}
        ]
        )
    else:
        
        curr_msgs = [
            {"role": "system", "content": "You are a helpful assistant designed to provide answers in markdown format to questions only based on context provided in natural, conversational manner."},
        ]
        
        n=5
        list_msgs = st.session_state.messages[-n:] if len(st.session_state.messages) >= n else st.session_state.messages
        
        for dict_n in list_msgs:
            curr_msgs.append(dict_n)
        
        curr_msgs.append({"role": "user", "content": query})
        print("Current Message hist:")
        print(curr_msgs)
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        # response_format={ "type": "json_object" },
        messages=curr_msgs
        )
    
    return response.choices[0].message.content
        
    
def fetch_context(query):

    url = "https://api.search.brave.com/res/v1/web/search"
    api_key = "BSAPEfWLRApnVtj1f1fLnG_PmNSg0lt"  # Replace <YOUR_API_KEY> with your actual API key

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    titles = query.split(',')
    print(titles)
    summarized_text = []
    
    for title in titles:
        params = {
            "q": title,
            "count": 3
        }

        response = requests.get(url, headers=headers, params=params)

        
        
        # # Send an HTTP GET request to the search engine
        urls = []
        if response.status_code == 200:
            results_dict = response.json()
            # Parse the HTML content of the search results page
            soup = BeautifulSoup(response.text, 'html.parser')
            attrs = [f"{val} \n\n" for val in soup.contents]
            for res in results_dict['web']['results']:
                urls.append(res['url'])

            for url in urls:
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # Extract all text from the HTML
                        all_text = soup.get_text()

                        # Print the extracted text
                        # print("="*100)
                        filtered_text = all_text.replace('\n'," ").replace('\t', " ").replace('  ', " ")
                        summary = openAI_api_call("Summarize", filtered_text)
                        # print(f"Filtered Text: {filtered_text}")
                        # print(f"Summarized Text: {summary}")
                        summarized_text.append(summary)
                        # print("="*100)
                except:
                    print(f"Invalid url : {url}")
        else:
            print("Failed to fetch real-time data. Status code:", response.status_code)
        
    return summarized_text

def fetch_images(query):

    url = "https://api.search.brave.com/res/v1/images/search"
    api_key = "BSAPEfWLRApnVtj1f1fLnG_PmNSg0lt"  # Replace <YOUR_API_KEY> with your actual API key

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }

    params = {
        "q": query,
        "count": 3
    }

    response = requests.get(url, headers=headers, params=params)

    # # Send an HTTP GET request to the search engine
    import json
    if response.status_code == 200:
        results_dict = response.json()
        # Parse the HTML content of the search results page
        soup = BeautifulSoup(response.text, 'html.parser')
        attrs = [f"{val} \n\n" for val in soup.contents]
        urls = []
        # print(soup.get_text())
        for res in results_dict['results']:
            urls.append(res['thumbnail']['src'])

        valid_urls = []
        for url in urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    valid_urls.append(url)
                    
                    # soup = BeautifulSoup(response.text, 'html.parser')

                    # # Extract all text from the HTML
                    # all_text = soup.get_text()

                    # # Print the extracted text
                    # # print("="*100)
                    # filtered_text = all_text.replace('\n'," ").replace('\t', " ").replace('  ', " ")
                    # summary = openAI_api_call("Summarize", filtered_text)
                    # # print(f"Filtered Text: {filtered_text}")
                    # # print(f"Summarized Text: {summary}")
                    # summarized_text.append(summary)
                    # print("="*100)
            except:
                print(f"Invalid url : {url}")
        return valid_urls
    else:
        print("Failed to fetch real-time data. Status code:", response.status_code)
        return []




def fetch_answer_from_bot(query, context):
    
    
    augmented_query = f"""
            Context: {context}

            Question: {query}
            
            Answer: 
    
    """
    
    # print("###"*10)
    # print(augmented_query)
    # print("###"*10)
    
    return openAI_api_call("Answer", augmented_query)


def display_imgs(urls):
    for url in urls:
        print(url)
        st.image(url, width = 100)


# while(True):
#     query = input("What would you like to know today?: ")

#     # context = fetch_context(query)
#     images = fetch_images(query)
    
#     # for c in context:
#     #     print("$$$$"*10)
#     #     print(f"Context is: {c}")
#     #     print("$$$$"*10)

#     # answer = fetch_answer_from_bot(query, context)

#     # print(answer)

import streamlit as st
import random
import time


# Streamed response emulator
def response_generator(answer):

    for word in answer.split():
        yield word + " "
        time.sleep(0.05)


st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to know today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    context = fetch_context(prompt)
    answer = fetch_answer_from_bot(prompt, context)
    img_query = openAI_api_call("img_search", answer)
    print("context :")
    print(context)
    print("context answer:")
    print(answer)
    print("img_query:")
    print(img_query)
    urls = fetch_images(img_query)
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(answer))
        display_imgs(urls)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})