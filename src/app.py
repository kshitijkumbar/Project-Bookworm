import gradio as gr
import os
import torch




from chain_generator import ChainGenerator
from model_loader import ModelLoader






from PIL import Image
from transformers import AutoProcessor, Blip2ForConditionalGeneration, AutoTokenizer, pipeline


import torch
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
search = DuckDuckGoSearchRun()
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
from langchain.embeddings import HuggingFaceEmbeddings
hf_embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma, FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import HuggingFacePipeline

from langchain.chains import RetrievalQA
from langchain.callbacks import StdOutCallbackHandler

import transformers




chain_generator = ChainGenerator()
model_loader = ModelLoader()

text_model, tokenizer = model_loader.getTextModel()
capt_model, processor = model_loader.getCaptionModel()

qa_with_sources_chain = chain_generator.getQAChain(text_model, tokenizer)


def add_text(history, text):
    # print(docsearch.similarity_search(text))
    answer = qa_with_sources_chain({'query':text})
    
    history = history + [(text, answer['result'])]
    return history, gr.Textbox(value="", interactive=False)


def add_file(history, file):
    # print(file.name)
    image = Image.open(file.name).convert('RGB')  
    device = "cuda" if torch.cuda.is_available() else "cpu"

    inputs = processor(image, return_tensors="pt").to(device, torch.float16)

    generated_ids = capt_model.generate(**inputs, max_new_tokens=20)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    print(f"The generated text is: {generated_text}")
    question = f"""Can you give me suggestions for a book that has {generated_text} on its cover?"""
    answer = qa_with_sources_chain({'query':question})
    print(answer['result'])
    history = history + [((file.name,), answer['result'])]
    return history


def bot(history):
    response = "**That's cool!**"
    yield history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
        )
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

demo.queue()
demo.launch(share=True)