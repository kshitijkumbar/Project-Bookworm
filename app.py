from pathlib import Path
import os
import openai
openai.api_key = os.getenv("OAI_KEY")
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import nest_asyncio

nest_asyncio.apply()



from llama_index.core import(SimpleDirectoryReader,
                            VectorStoreIndex, StorageContext,
                            Settings,set_global_tokenizer)

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from transformers import AutoTokenizer, BitsAndBytesConfig
from llama_index.llms.huggingface import HuggingFaceLLM
import torch
import logging
import sys
import streamlit as st
import os
from llama_index.core import load_index_from_storage


Settings.llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.2)
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-large", embed_batch_size=100
)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def getDocs(doc_path="./data/"):
    documents = SimpleDirectoryReader(doc_path).load_data()
    return documents


def getVectorIndex():
    Settings.chunk_size = 512
    index_set = {}
    if os.path.isdir(f"./storage/open_ai_embedding_data_large"):
        print("Index already exists")
        storage_context = StorageContext.from_defaults(
        persist_dir=f"./storage/open_ai_embedding_data_large"
        )
        cur_index = load_index_from_storage(
            storage_context,
        )
    else:
        print("Index does not exist, creating new index")
        docs = getDocs()
        storage_context = StorageContext.from_defaults()
        cur_index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
        storage_context.persist(persist_dir=f"./storage/open_ai_embedding_data_large")
    return cur_index

def getQueryEngine(index):
    query_engine = index.as_chat_engine()
    return query_engine










st.set_page_config(page_title="Project BookWorm: Your own Librarian!", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Project BookWorm: Your own Librarian!")
st.info("Use this app to get recommendations for books that your kids will love!", icon="📃")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about children's books or movies!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    index = getVectorIndex()
    return index
import time
s_time = time.time()
index = load_data()
e_time = time.time()

print(f"It took {e_time - s_time} to load index")

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_plus_context", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history

















# if __name__ == "__main__":

#     index = getVectorIndex(getDocs())
#     query_engine = getQueryEngine(index)
#     while(True):
#         your_request = input("Your comment: ")
#         response = query_engine.chat(your_request)
#         print(response)









    
