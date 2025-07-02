import streamlit as st
from fastapi import FastAPI,Request
import openai
from langchain.chains.question_answering.map_rerank_prompt import output_parser
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
import math

app =FastAPI()

origins = [
    "http://localhost:3000",  # Local React app
    "https://chatbot-woad-alpha.vercel.app",  # Your production frontend domain
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
items=[{"id":1,"name":"shikhar"},{"id":2,"name":"kiran"}]


prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are a dumb assistant. answer questions with more stupid questions"),
        ("user","Question:{question}")
    ]
)

temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7)
max_tokens = st.sidebar.slider("Max Tokens", min_value=50, max_value=300, value=150)

def get_response(question,llm,temp,max_token):
    newmodel=Ollama(model=llm)
    output_parser=StrOutputParser()
    chain=prompt|newmodel|output_parser
    result=chain.invoke({"question":question})
    return result

@app.get("/items")
def get_items():
    return items

@app.post("/item/")
def add_item(request:Request):
    body=request.json()
    answer=get_response(body,"mistral",temperature,max_tokens)
    return answer
