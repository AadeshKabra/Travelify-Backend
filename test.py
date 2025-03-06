from serpapi import GoogleSearch

params = {
  "engine": "google_flights",
  "departure_id": "PNQ",
  "arrival_id": "BLR",
  "outbound_date": "2025-03-08",
  "currency": "INR",
  "hl": "en",
  "api_key": "4c877630ce1fd306bb061697b2df107b019479d69d93e2cdb60efca53cc8b8c5",
  "type": "2"
}
# "hl": "en",
search = GoogleSearch(params)
results = search.get_dict()
print(results)

# "4c877630ce1fd306bb061697b2df107b019479d69d93e2cdb60efca53cc8b8c5"

# emxKw5OA0sk0Fr2YLGhx/w==ECpFRtFnZI2hmjIw
# import requests
#
# name = "London Heathrow"
# api_url = "https://api.api-ninjas.com/v1/airportslist"
#
# response = requests.get(api_url, headers={'X-Api-Key': "emxKw5OA0sk0Fr2YLGhx/w==ECpFRtFnZI2hmjIw"})
# if response.status_code == requests.codes.ok:
#   print(response.text)
# else:
#   print(response.status_code)


# import requests
#
# url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport"
#
# querystring = {"query":"singapore","locale":"en-US"}
#
# headers = {
# 	"x-rapidapi-key": "631f11fb00msh46d68d29c19c432p173cdajsna4808c3da14c",
# 	"x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
# }
#
# response = requests.get(url, headers=headers, params=querystring)
#
# # print(response.json())
# for item in response.json()["data"]:
# 	print(item)

# import requests
#
# url = "https://sky-scanner3.p.rapidapi.com/flights/airports"
#
# headers = {
# 	"x-rapidapi-key": "631f11fb00msh46d68d29c19c432p173cdajsna4808c3da14c",
# 	"x-rapidapi-host": "sky-scanner3.p.rapidapi.com"
# }
#
# response = requests.get(url, headers=headers)
#
# # print(response.json())
# for item in response.json()["data"]:
# 	print(item)


# import http.client
#
# conn = http.client.HTTPSConnection("sky-scanner3.p.rapidapi.com")
#
# headers = {
#     'x-rapidapi-key': "631f11fb00msh46d68d29c19c432p173cdajsna4808c3da14c",
#     'x-rapidapi-host': "sky-scanner3.p.rapidapi.com"
# }
#
# conn.request("GET", "/flights/auto-complete?query=New%20York", headers=headers)
#
# res = conn.getresponse()
# data = res.read()
#
# print(data.decode("utf-8"))