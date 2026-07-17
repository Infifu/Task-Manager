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
from models import *
from datetime import datetime

Base.metadata.create_all(bind=database.engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Pydantic creates init for the class
class ResponseTask(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=1000)
    date_created: datetime
    status: str

    model_config = {
        "from_attributes": True
    }


class RequestTask(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=100)


id_count = 2


@app.get("/")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    tasks = db.query(Tasks).all()
    print(tasks)
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "tasks": tasks,
        }
    )


@app.get("/tasks/{task_id}")
def read_task(task_id: int, request: Request, db: Annotated[Session, Depends(get_db)]):
    task = db.get(Tasks, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse(
        request=request,
        name="task.html",
        context={
            "task": task,
        }
    )


@app.get("/api/tasks/{task_id}",response_model=ResponseTask)
def read_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.get(Tasks, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


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


@app.post("/api/tasks", response_model=ResponseTask, status_code=status.HTTP_201_CREATED)
def create_task(task: RequestTask, db: Annotated[Session, Depends(get_db)]):
    newTask = Tasks(
        title=task.title,
        content=task.content,
        date_created=datetime.now(UTC),
        user_id=1,
        status="To Do"
    )
    db.add(newTask)
    db.commit()
    db.refresh(newTask)
    print(task)
    return newTask


@app.delete("/api/{task_id]", status_code=status.HTTP_200_OK)
def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.get(Tasks, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
