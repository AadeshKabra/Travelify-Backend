import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import uvicorn
import json
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from serpapi import GoogleSearch
from google import genai


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_FILE_PATH = os.getenv("TOKEN_FILE_PATH")
CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE")
FRONTEND_URL = os.getenv("FRONTEND_URL")
FLIGHT_SEARCH_API_KEY = os.getenv("FLIGHT_SEARCH_API_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
with open(CLIENT_SECRET_FILE, "r") as f:
    data = json.load(f)
    GOOGLE_CLIENT_ID = data["installed"]["client_id"]
    GOOGLE_CLIENT_SECRET = data["installed"]["client_secret"]
    GOOGLE_REDIRECT_URI = data["installed"]["redirect_uris"][0] + ":8000/auth/google"


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.get("/demo")
async def demo():
    print("Reached backend")
    return {"Reached": "Backend"}


@app.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }


@app.get("/auth/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})

    frontend_redirect_url = f"{FRONTEND_URL}?name={user_info.json()['name']}&email={user_info.json()['email']}"
    # print(user_info.json()["name"], user_info.json()["email"])
    return RedirectResponse(url=frontend_redirect_url)


@app.post("/getFlights")
async def get_flights(payload: dict):
    data = payload["params"]
    departure = data["departure"]
    arrival = data["arrival"]
    date = data["date"]

    departure_iata = departure.split(" - ")[0]
    arrival_iata = arrival.split(" - ")[0]

    params = {
        "engine": "google_flights",
        "departure_id": departure_iata,
        "arrival_id": arrival_iata,
        "outbound_date": date,
        "type": "2",
        "currency": "INR",
        "api_key": FLIGHT_SEARCH_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    best_flights = results["best_flights"]
    other_flights = results["other_flights"]


    return JSONResponse(content={
        "best_flights": best_flights,
        "other_flights": other_flights,
        "status": "success"
    })


@app.post("/searchHotels")
async def search_hotels(payload: dict):
    # print(payload)
    destination = payload["destination"]
    checkin = payload["checkinDate"]
    checkout = payload["checkoutDate"]
    adults = payload["adults"]
    children = payload["children"]

    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": checkin,
        "check_out_date": checkout,
        "adults": adults,
        "children": children,
        "currency": "INR",
        "gl": "in",
        "hl": "en",
        "api_key": FLIGHT_SEARCH_API_KEY,
        "num": 20
    }
    # print(params)
    children_ages = ""
    if children!='':
        for i in range(int(children)-1):
            children_ages += "17, "
        children_ages += "17"

    # print(children_ages)
    params["children_ages"] = children_ages

    search = GoogleSearch(params)
    results = search.get_dict()

    # print(results)
    # for item in results:
    #     print(item, "=>", results[item])
    #     print("=======================================")

    # return JSONResponse(content={"message": "received"})
    return JSONResponse(content=results)


@app.post("/getHotelInformation")
async def get_hotel_information(data: dict):
    payload = data["payload"]
    property_token = data["property_token"]
    name = data["name"]
    # print(payload, property_token)

    params = {
        "engine": "google_hotels",
        "q": name,
        "check_in_date": payload["checkinDate"],
        "check_out_date": payload["checkoutDate"],
        "adults": payload["adults"],
        "children": payload["children"],
        "currency": "INR",
        "property_token": property_token,
        "api_key": FLIGHT_SEARCH_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    # print(results)
    for item in results:
        print(item)


    image_params = {
        "q": name,
        "engine": "google_images",
        "ijn": "0",
        "api_key": FLIGHT_SEARCH_API_KEY
    }
    images_search = GoogleSearch(image_params)
    images_results = images_search.get_dict()["images_results"]
    # images_results = results["images_results"]
    response = {
        "hotel_information": results,
        "hotel_images": images_results
    }
    return JSONResponse(content=response)


@app.post("/submitIternary")
async def submit_iternary(payload: dict):
    data = payload["params"]

    return Response(content="iternary received in backend", media_type="text/plain")




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)