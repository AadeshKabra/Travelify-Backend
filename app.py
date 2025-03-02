import os
from fastapi import FastAPI, requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi.security import OAuth2PasswordBearer



app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"Hello": "World"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)