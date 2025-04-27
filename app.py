import asyncio
import io
import os
from fastapi import FastAPI, Response, UploadFile, File
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
from datetime import datetime, timedelta
import PIL.Image
from PIL import Image
import spacy


def get_hotels(destination, checkin, checkout, adults, children, min_price, max_price):
    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": checkin,
        "check_out_date": checkout,
        "adults": adults,
        "children": children,
        "min_price": min_price,
        "max_price": max_price,
        "currency": "INR",
        "gl": "in",
        "hl": "en",
        "api_key": FLIGHT_SEARCH_API_KEY,
        "num": 10,
        "sort_by": 3
    }
    # print(params)
    children_ages = ""
    if children != '':
        for i in range(int(children) - 1):
            children_ages += "17, "
        children_ages += "17"

    # print(children_ages)
    params["children_ages"] = children_ages

    search = GoogleSearch(params)
    results = search.get_dict()

    return results


def get_gemini_response(destination, checkin, checkout, adults, children, min_price, max_price, interests, description, hotels):
    prompt = f"""
    Consider yourself as an automated travel itinerary planner which helps in planning travels for a user. Give just the itinerary in the response.
    I have few details for your references to generate the itinerary. 
    Destination: {destination}
    Checkin Date: {checkin}
    Checkout Date: {checkout}
    Min. Budget for the trip: {min_price}
    Max. Budget for the trip: {max_price}
    There are {adults} adults and {children} children who would be travelling.
    You can plan itinerary based on list of user-interests as follows: {interests}. Make sure to use this interests to plan the itinerary.
    Below is the list of hotels fetched according to the user's budget: {hotels}.
    There is also some additional description for the trip as follows:
    {description}
    You can use these hotels to plan the stay.
    Give me a complete day-wise splitted travel itinerary.
    """

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text


def extract_location(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
    return locations[0] if locations else "Location not found"


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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_DATA = json.loads(os.getenv("GOOGLE_API_DATA"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# print(GOOGLE_API_DATA)
# print(type(GOOGLE_API_DATA))
# print(GOOGLE_CLIENT_ID)

GOOGLE_CLIENT_ID = GOOGLE_API_DATA["installed"]["client_id"]
GOOGLE_CLIENT_SECRET = GOOGLE_API_DATA["installed"]["client_secret"]
GOOGLE_REDIRECT_URI = GOOGLE_API_DATA["installed"]["redirect_uris"][0] + ":8000/auth/google"

# with open(CLIENT_SECRET_FILE, "r") as f:
#     data = json.load(f)
#     GOOGLE_CLIENT_ID = data["installed"]["client_id"]
#     GOOGLE_CLIENT_SECRET = data["installed"]["client_secret"]
#     GOOGLE_REDIRECT_URI = data["installed"]["redirect_uris"][0] + ":8000/auth/google"


nlp = spacy.load("en_core_web_sm")

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

    # results = get_hotels(destination, checkin, checkout, adults, children)
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
        "num": 10,
        "sort_by": 3
    }

    search = GoogleSearch(params)
    results = search.get_dict()

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
    # print(data)
    destination = data["destination"]
    checkin = data["date"]
    adults = data["adults"]
    children = data["children"]
    checkout = (datetime.strptime(checkin, "%Y-%m-%d") + timedelta(days=int(data["days"]))).strftime("%Y-%m-%d")
    min_price = int(data["minBudget"])
    max_price = int(data["maxBudget"])
    interests = data["interests"]
    description = data["description"]

    weights = {
        "Luxury": {"Hotel": 0.45, "Transport": 0.25, "Food": 0.20, "Activities": 0.5, "Misc": 0.5},
        "Adventure": {"Hotel": 0.30, "Transport": 0.30, "Food": 0.15, "Activities": 0.20, "Misc": 0.5},
        "Backpacking": {"Hotel": 0.20, "Transport": 0.40, "Food": 0.15, "Activities": 0.20, "Misc": 0.5},
        "Spiritual": {"Hotel": 0.30, "Transport": 0.30, "Food": 0.15, "Activities": 0.20, "Misc": 0.5},
        "Business": {"Hotel": 0.30, "Transport": 0.30, "Food": 0.20, "Activities": 0.15, "Misc": 0.5},
        "Romantic": {"Hotel": 0.25, "Transport": 0.25, "Food": 0.20, "Activities": 0.25, "Misc": 0.5},
        "Cultural": {"Hotel": 0.25, "Transport": 0.20, "Food": 0.20, "Activities": 0.20, "Misc": 0.15}
    }

    if len(interests)==0:
        hotel_weights = 0.25
        transport_weights = 0.20
        food_weights = 0.20
        activities_weights = 0.20
        misc = 0.15

        min_hotel_price = int(int(hotel_weights * min_price)/int(data["days"]))
        max_hotel_price = int(int(hotel_weights * max_price)/int(data["days"]))
        print("Min: ", min_hotel_price)
        print("Max: ", max_hotel_price)
        hotel_results = get_hotels(destination, checkin, checkout, adults, children, min_hotel_price, max_hotel_price)
    else:
        hotel_weights = 0
        for interest in interests:
            hotel_weights += weights[interest]["Hotel"]

        hotel_weights = float(hotel_weights / len(interests))
        min_hotel_price = int(int(hotel_weights * min_price)/int(data["days"]))
        max_hotel_price = int(int(hotel_weights * max_price)/int(data["days"]))
        print("Min: ", min_hotel_price)
        print("Max: ", max_hotel_price)
        hotel_results = get_hotels(destination, checkin, checkout, adults, children, min_hotel_price, max_hotel_price)


    # print(hotel_results)
    # print("==================================================")
    hotels = []
    for hotel in hotel_results["properties"]:
        # print(hotel)
        hotels.append({"Hotel Name": hotel["name"], "Hotel Price": hotel["rate_per_night"]["lowest"]})
        # print("-----------------------------------------------")

    # results = get_hotels(destination, checkin, checkout, adults, children, min_price, max_price)
    # print(results)
    result = get_gemini_response(destination, checkin, checkout, adults, children, min_price, max_price, interests, description, hotels)
    results = {"result": result}

    return JSONResponse(content=results)


@app.post("/picture2Place")
async def picture_2_place(image: UploadFile = File(...)):
    contents = await image.read()
    image_stream = io.BytesIO(contents)
    img = Image.open(image_stream)
    print(f"Received image: {image.filename}, Type: {image.content_type}")

    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format=img.format)
    img_bytes = img_byte_array.getvalue()

    client = genai.Client(api_key=GEMINI_API_KEY)
    # response = client.models.generate_content(model="gemini-2.0-flash", contents=["Can you identify and describe the location of this image?", img])
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: client.models.generate_content(
        model = "gemini-2.0-flash",
        contents = ["Can you identify and describe the location of this image?", img]
    ))

    result_text = response.text if hasattr(response, "text") else "No response received"
    location = extract_location(result_text)
    print(response.text)
    print(location)
    results = {"result": result_text, "Location": location}

    return JSONResponse(content=results)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)