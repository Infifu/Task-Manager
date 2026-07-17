from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from typing import Annotated

import database
from database import get_db

import tools
import models
from datetime import datetime

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Pydantic creates init for the class
class Task(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=1000)
    date: str
    status: str


class RequestTask(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=100)


id_count = 2

tasks: list[Task] = [
    Task(id=1,
         title="Clean the house",
         content="do a deep cleaning",
         date="July 15, 2026",
         status="In Progress"),
    Task(id=2,
         title="Wash the dishes",
         content="Wash the pan",
         date="July 15, 2026",
         status="In Progress")
]


@app.get("/")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    taskss = db.query(models.Tasks).all()
    print(tasks)
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "tasks": tasks,
        }
    )


@app.get("/tasks/{task_id}")
def read_task(task_id: int, request: Request):
    for task in tasks:
        if task.id == task_id:
            return templates.TemplateResponse(
                request=request,
                name="task.html",
                context={
                    "task": task,
                }
            )
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/api/tasks/{task_id}")
def read_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return {"title": task.title, "content": task.content}
    raise HTTPException(status_code=404, detail="Task not found")


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"status_code": exception.status_code, "detail": exception.detail},
        )
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


@app.post("/api/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: RequestTask):
    global id_count
    id_count += 1
    newTask = Task(
        id=id_count,
        title=task.title,
        content=task.content,
        date=tools.format_date(datetime.now()),
        status="To Do"
    )

    tasks.append(newTask)
    return newTask


@app.delete("/api/{task_id]", status_code=status.HTTP_200_OK)
def delete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return {"content": "task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")
