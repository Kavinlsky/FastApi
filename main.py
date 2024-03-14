from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
# import models
# from database import engine, sessionlocal
# from sqlalchemy.orm import Session

from fastapi import responses
# from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse

# from forms import UserCreateForm

# models.Base.metadata.create_all(bind=engine)

templates=Jinja2Templates(directory="templates")

app=FastAPI()


@app.get("/")
async def home(request : Request):
    return templates.TemplateResponse('index.html',{"request":request})


@app.post("/register/")
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
                   # db: Session = Depends(get_db)):
    # form = UserCreateForm(request)
    # await form.load_data()
    # print("submited")
    # if await form.is_valid():
        try:
            print(username)
            print(email)
            print(password)
        except:
            pass

    #         total_row = db.query(models.User).filter(models.User.email == email).first()
    #         print(total_row)
    #         if total_row == None:
    #             print("Save")
    #             users = models.User(username=username, email=email, password=password)
    #             db.add(users)
    #             db.commit()
    #
    #             return responses.RedirectResponse(
    #                 "/", status_code=status.HTTP_302_FOUND
    #             )
    #         else:
    #             print("taken email")
    #             errors = ["The email has already been taken"]
    #
    #     except IntegrityError:
    #         return {"msg": "Error"}
    # else:
    #     print("Error Form")
    #     errors = form.errors
    #
    # return templates.TemplateResponse("index.html", {"request": request, "errors": errors})