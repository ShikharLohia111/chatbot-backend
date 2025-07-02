import streamlit as st
from fastapi import FastAPI,Request
import openai
from langchain.chains.question_answering.map_rerank_prompt import output_parser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from fastapi.middleware.cors import CORSMiddleware
import math
import json

import os
from dotenv import load_dotenv
load_dotenv()

app =FastAPI()

os.environ["LANGCHAIN_API_KEY"]="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"
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="Simple Q&A Chatbot With Ollama"

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

temperature=0.7
max_tokens = 150

def get_response(question,llm,temp,max_token):
    newmodel=OllamaLLM(model="llama3.1")
    output_parser=StrOutputParser()
    chain=prompt|newmodel|output_parser
    result=chain.invoke({"question":question})
    return result

@app.get("/items")
def get_items(ques:str):
    body = ques
    answer = get_response(body, "llama3.1", temperature, max_tokens)
    return answer

@app.post("/item/")
async def add_item(request:Request):
    body=await request.json()
    answer=get_response(body,"llama3.1",temperature,max_tokens)
    return answer

