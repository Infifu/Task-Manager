from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

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
