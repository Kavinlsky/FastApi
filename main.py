from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import openai

templates=Jinja2Templates(directory="templates")

app=FastAPI()


class Message(BaseModel):
    message: str


@app.get("/")
async def home(request : Request):
    return templates.TemplateResponse('index.html',{"request":request})


@app.post("/register/")
async def register(request: Request, companyname: str = Form(...), address: str = Form(...), pan: str = Form(...), aadhar: str = Form(...),password:str = Form(...)):

    try:
        print(companyname)
        print(address)
        print(pan)
        print(aadhar)
        print(password)
        message="Successfully Registered, You can click Login "
        return templates.TemplateResponse("index.html", {"request": request, "message": message})
    except:
        pass

@app.get("/login")
async def login(request : Request):
    return templates.TemplateResponse('login.html',{"request":request})


@app.post("/login_authenticate")
async def authenticate(request: Request, companyname: str = Form(...), password: str = Form(...)):
    print(companyname, password)

    return templates.TemplateResponse('chat.html', {"request": request})

@app.post("/api/chat")
async def chat_with_bot(message: Message):

    print(message)

    return {"response": message.message}
