from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI()

templates = Jinja2Templates(directory="templates")

tasks: list[dict] = [
    {
        "id": 1,
        "title": "clean the house",
        "content": "do a deep cleaning",
        "date": "July 15, 2026",
        "status": "In Progress"
    },
    {
        "id": 2,
        "title": "wash the dishes",
        "content": "wash the pam",
        "date": "July 15, 2026",
        "status": "In Progress"
    },
]


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "tasks": tasks,
        }
    )


@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return {"title": task["title"], "content": task["content"]}
    raise HTTPException(status_code=404, detail="Task not found")


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "error": exception
        }
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    error = {
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "detail": exception.errors()[0]["msg"]
    }
    print(error)
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "error": error
        }
    )
