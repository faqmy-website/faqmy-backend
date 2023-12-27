from fastapi import FastAPI

from faqmy_backend.app.builder import build_app

app = FastAPI()
app = build_app(app)
