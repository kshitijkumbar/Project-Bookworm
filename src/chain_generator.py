from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFacePipeline

from langchain.chains import RetrievalQA
from langchain.callbacks import StdOutCallbackHandler
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma, FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import HuggingFacePipeline
from langchain.globals import set_debug

from transformers import (
    pipeline,

)




class ChainGenerator:

    def __init__(self):
        self.separator = "\n"
        self.chunk_size = 400
        self.chunk_overlap  = 50

    def getChainTypeArgs(self):
        """
            Get Chain Type arguments for QA chain
        """
        prompt_template = """If the request is for a suggestion or request for names, only use the following pieces of context to complete the request at the end. 
                            If the request is for a summary or something alike, respond by saying that the feature requires Wikipedia and do not provide an answer after Answer: . 

        {context}

        Request: {question}
        Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )


        chain_type_kwargs = {"prompt": PROMPT}

        return chain_type_kwargs

        
    def getQARetriever(self, embed_model = None, data_path = None):
        """
            Get Langchain retriever from vector store for QA Chain
        """
        if data_path:
            with open(data_path) as f:
                book_ds = f.read()
        else:
            with open('../book_ds.txt') as f:
                book_ds = f.read()

        text_splitter = CharacterTextSplitter(        
            separator = self.separator,
            chunk_size = self.chunk_size,
            chunk_overlap  = self.chunk_overlap,
            length_function = len,
        )
        texts = text_splitter.create_documents([book_ds])
        if embed_model:
            hf_embeddings = HuggingFaceEmbeddings(model_name=embed_model)
        else:
            hf_embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        
        docsearch = Chroma.from_documents(texts, hf_embeddings)        
        retriever = docsearch.as_retriever()

        return retriever

    def getHFPipeline(self, model, tokenizer):
        ans_pipeline = pipeline(
                        model=model,
                        tokenizer=tokenizer,
                        task="text-generation",
                        return_full_text=True,
                        temperature=0.0000001,
                        max_new_tokens=256
                        )
        llm = HuggingFacePipeline(pipeline=ans_pipeline)
        
        return llm

    def getQAChain(self, model, tokenizer):
        """
            Get QA chain based on model and relevant tokenizer
        """
        
        llm = self.getHFPipeline(model, tokenizer)
        retriever = self.getQARetriever()
        handler = StdOutCallbackHandler()
        chain_type_kwargs = self.getChainTypeArgs()
        
        qa_with_sources_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            callbacks=[handler],
            return_source_documents=True,
            chain_type_kwargs=chain_type_kwargs
        )

        return qa_with_sources_chain

