from fastapi import FastAPI, Request, Depends, Form, status, HTTPException,Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
import google.generativeai as genai
import os
import pymongo
from typing import List
from pymongo.results import UpdateResult



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

class ProfileUpdate(BaseModel):
    company: str
    address: str
    pan: str
    aadhar: str
    password: str


class ProfileDelete(BaseModel):
    company: str
    

class CompanyRequest(BaseModel):
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


@app.get("/api/chat/history/{company_name}", response_model=List[dict])
async def get_chat_history(company_name: str):
    collection = database["chats"]
    chat_history = collection.find({"company": company_name})
    response_data=[]
    if chat_history:
        for document in chat_history:
            user=document.get("question")
            server=document.get("result")
            response_data.append({'user':user,'server':server})
        return response_data
   

@app.get('/edit')
def edit_profile(request : Request):
    company_name = request.query_params.get("company")
    collection = database["company"]
    company_profile = collection.find({"company": company_name})
   
    company_profile=list(company_profile)[0]
    return templates.TemplateResponse('edit.html', {"request": request, "company_profile": company_profile})


@app.post("/update_profile")
async def update_profile(profile_update: ProfileUpdate):
    profile_data = profile_update.dict()
    collection = database["company"]
  
    result: UpdateResult = collection.update_one(
        {},
        {"$set": profile_data}
    )
    if result:
         print(result)
   
         return {"message": "Profile updated successfully"}
    

@app.post("/delete_profile")
async def delete_profile(delete_profile: ProfileDelete):
    print("Received profile delete:", delete_profile)
    company=delete_profile.company
    collection = database["company"]
    result = collection.delete_one({"company": company})
    if result.deleted_count == 1:
        return {"message": "Record deleted successfully"}
    else:
        return {"message": "Record not found"}


@app.post("/clear_chat")
async def clear_chat(request: CompanyRequest):
     
    company_name=request.company
    collection = database["chats"]
    result = collection.delete_many({"company": company_name})
    print(result)
    if result.deleted_count > 0:
        return {"message": f"Chat history for {company_name} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"No chat history found for {company_name}")
