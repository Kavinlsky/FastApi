from fastapi import FastAPI, Request, Depends, Form, status, HTTPException,Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
import google.generativeai as genai
import os
import pymongo
# from fastapi.session import Session


mongo_host = "localhost"
mongo_port = 27017
database_name = "fastapi"
client = pymongo.MongoClient(mongo_host, mongo_port)

database = client[database_name]
collection = database["company"]

google_api_key="AIzaSyCb7qViOgJSBKv_dlNtJl2wciagQ7K6AEY"
os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=google_api_key)

templates=Jinja2Templates(directory="templates")

app=FastAPI()
client=OpenAI(api_key='OPENAI-API-KEY')


class Message(BaseModel):
    message: str
    company: str


def get_session(request: Request):
    return request.session

@app.get("/")
async def home(request : Request):
    return templates.TemplateResponse('index.html',{"request":request})


@app.post("/register/")
async def register(request: Request, companyname: str = Form(...), address: str = Form(...), pan: str = Form(...), aadhar: str = Form(...),password:str = Form(...)):
    try:
        existing_company = collection.find_one({"company": companyname})
        if existing_company:
            message = f"Company '{companyname}' already exists. Please choose a different name."
            return templates.TemplateResponse("index.html", {"request": request, "message": message})

        document = {
            "company": companyname,
            "address": address,
            "pan": pan,
            "aadhar": aadhar,
            "password": password
        }
        collection.insert_one(document)

        message=f"Successfully Registered {companyname}, You can click Login "
        return templates.TemplateResponse("index.html", {"request": request, "message": message})
    except:
        pass


@app.get("/login")
async def login(request : Request):
    return templates.TemplateResponse('login.html',{"request":request})


@app.post("/login_authenticate")
async def authenticate(request: Request, companyname: str = Form(...), password: str = Form(...)):
    user = collection.find_one({"company": companyname, "password": password})

    if user is None:
        message=f'Invalid Credentials'
        return templates.TemplateResponse('login.html', {"request": request, "message": message})

    return templates.TemplateResponse('chat.html',{"request": request, "company": companyname})


def response_from_gemini(question):
    prompt = """You are an AI assistant. You're tasked with asking dynamic questions to gather information. Your 
    questions should cover topics such as the company's type (service/product-based), goals for the next 5 years, 
    and inspiration."""
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + " " + question)
    result = response.text
    return result


def response_from_openai(question):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": """You are an AI assistant. Asking dynamic questions to gather information.
                            To ask dynamic questions such as the company's type (service/product-based),
                            goals for the next 5 years, and inspiration."""},
            {"role": "user", "content": f'Context: {question}'},
        ]
    )
    result = response.choices[0].message.content
    return result


@app.post("/api/chat")
async def chat_with_bot(message: Message):
    company_name=message.company
    message=message.message

    # result= response_from_openai(message)
    result=response_from_gemini(message)
    chat_collection = database["chats"]
    document = {
        "company": company_name,
        "question": message,
        "result":result
    }
    chat_collection.insert_one(document)

    return {"response":result}
