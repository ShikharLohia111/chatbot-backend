import streamlit as st
from fastapi import FastAPI
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

@app.get("/items")
def get_items():
    return items

@app.post("/item/")
def add_item(it:dict):
    items.append(it)
    return items

# st.title("i dont know what to do")
# st.write("First program")
#
# name=st.text_input("Whats your name?")
# print(name+" first program")
#
# def prime(num):
#     temp=int(num)
#     count=0
#     for i in range(2,int(math.sqrt(temp))):
#         if temp%2==0:
#             count=1
#             break
#
#     if count==0:
#         st.write("prime")
#     else:
#         st.write(" not prime")
#
#
# if name.isnumeric():
#     prime(name)
# else:
#     st.write("Write in digit")
