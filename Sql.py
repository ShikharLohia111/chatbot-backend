import streamlit as st
import pandas as pd
import psycopg2
from io import BytesIO
from fastapi.responses import JSONResponse
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
import ollama
import json
import requests
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

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
temperature=0.7
max_tokens = 150

promptquery=ChatPromptTemplate.from_messages(
    [
        ("system",'''These are the schema to run the commands on:
        CREATE TABLE employee (emp_id SERIAL PRIMARY KEY,         -- Unique Employee ID (auto-incrementing)
        first_name VARCHAR(50) NOT NULL,    -- Employee's first name
        last_name VARCHAR(50) NOT NULL,     -- Employee's last name
        email VARCHAR(100) UNIQUE NOT NULL, -- Employee's email (unique constraint)
        phone_number VARCHAR(15),           -- Employee's phone number (optional)
        hire_date DATE NOT NULL,            -- Employee's hire date
        salary NUMERIC(10, 2) CHECK (salary > 0), -- Employee's salary (positive values only)
        department VARCHAR(50),             -- Department the employee works in (optional)
        position VARCHAR(50),               -- Position/role of the employee
        CONSTRAINT emp_email_format   -- Email format check
        )
        CREATE TABLE manager (manager_id SERIAL PRIMARY KEY,         -- Unique Manager ID (auto-incrementing)
        emp_id INT NOT NULL,                   -- Reference to employee ID (foreign key)
        start_date DATE NOT NULL,              -- The date the manager became a manager
        department VARCHAR(50),                -- Department the manager oversees
        FOREIGN KEY (emp_id) REFERENCES employee (emp_id) ON DELETE CASCADE  -- Foreign key link to employee);
        '''),
        ("user","Question:{question}")
    ]
)
promptdesc=ChatPromptTemplate.from_messages(
    [
        ("system","Explain in very brief what the mentioned sql query will do when executed"),
        ("user","Question:{question}")
    ]
)
def get_response(question,llm,temp,max_token,typeprompt):
    newmodel=OllamaLLM(model=llm)
    output_parser=StrOutputParser()
    if typeprompt=='desc':
        chain=promptdesc|newmodel|output_parser
    else:
        chain=promptquery|newmodel|output_parser
    result=chain.invoke({"question":question})
    return result

def get_query(ques:str):
    question=ques
#     data={
#
#         "model":"duckdb-nsql",
#         "messages":[{"role":"system","content":'''This is the schema to run the commands on CREATE TABLE employee (
#     emp_id SERIAL PRIMARY KEY,         -- Unique Employee ID (auto-incrementing)
#     first_name VARCHAR(50) NOT NULL,    -- Employee's first name
#     last_name VARCHAR(50) NOT NULL,     -- Employee's last name
#     email VARCHAR(100) UNIQUE NOT NULL, -- Employee's email (unique constraint)
#     phone_number VARCHAR(15),           -- Employee's phone number (optional)
#     hire_date DATE NOT NULL,            -- Employee's hire date
#     salary NUMERIC(10, 2) CHECK (salary > 0), -- Employee's salary (positive values only)
#     department VARCHAR(50),             -- Department the employee works in (optional)
#     position VARCHAR(50),               -- Position/role of the employee
#     CONSTRAINT emp_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')  -- Email format check
# );
# CREATE TABLE manager (
#     manager_id SERIAL PRIMARY KEY,         -- Unique Manager ID (auto-incrementing)
#     emp_id INT NOT NULL,                   -- Reference to employee ID (foreign key)
#     start_date DATE NOT NULL,              -- The date the manager became a manager
#     department VARCHAR(50),                -- Department the manager oversees
#     FOREIGN KEY (emp_id) REFERENCES employee (emp_id) ON DELETE CASCADE  -- Foreign key link to employee
# );'''},
#                      {"role":"user","content":question}],
#         "stream":False
#     }
#     url="http://localhost:11434/api/chat"
#     response=requests.post(url,json=data)
#     response=json.loads(response.text)
#     response=response["message"]["content"]
    response=get_response(question,'duckdb-nsql',temperature,max_tokens,"query")
    val=st.text_input("Edit the query",value=response)
    st.write("above query will behave in the following way: " +get_description(val))
    return val

def get_description(text:str):
    question=text
    # data={
    #
    #     "model":"llama3.1",
    #     "messages":[{"role":"system","content":"Explain in very brief what the mentioned sql query will do when executed"},
    #                  {"role":"user","content":question}],
    #     "stream":False
    # }
    # url="http://localhost:11434/api/chat"
    # response=requests.post(url,json=data)
    # response=json.loads(response.text)
    # response=response["message"]["content"]
    response=get_response(question,'llama3.1',temperature,max_tokens,"desc")

    return response


# Function to connect to PostgreSQL and fetch data
def get_data_from_postgresql(ques:str):
    try:
        # Set up the connection to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",  # Replace with your PostgreSQL host
            dbname="postgres",  # Replace with your database name
            user="postgres",  # Replace with your database username
            password="zxcasdqwE@1"  # Replace with your password
        )

        # Define the query to fetch your table
        query = get_query(ques)  # Replace 'your_table' with your actual table name

        # Load the table into a pandas dataframe
        df = pd.read_sql(query, conn)

        # Close the connection
        conn.close()

        return df

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


# Function to download dataframe as CSV
def to_csv(df):
    csv = df.to_csv(index=False)
    return csv.encode()


# Function to download dataframe as Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


# Streamlit UI
st.title("PostgreSQL Table Viewer")

# Fetch data from PostgreSQL
queryprompt=st.text_input("Enter the query")
df = get_data_from_postgresql(queryprompt)

# Check if data was retrieved
if df is not None:
    st.dataframe(df)  # Display dataframe in the app

    # Create download buttons
    st.subheader("Download Data")

    # CSV download
    csv = to_csv(df)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="table_data.csv",
        mime="text/csv"
    )

    # Excel download
    excel = to_excel(df)
    st.download_button(
        label="Download Excel",
        data=excel,
        file_name="table_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.error("Could not retrieve data from the database.")
