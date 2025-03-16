# from serpapi import GoogleSearch
#
# params = {
#   "engine": "google_hotels",
#   "q": "Bali Resorts",
#   "check_in_date": "2025-03-13",
#   "check_out_date": "2025-03-14",
#   "adults": "2",
#   "currency": "USD",
#   "gl": "us",
#   "hl": "en",
#   "property_token": "ChcI9uq9hrWO2OtjGgsvZy8xMjJ0YzFteBAB",
#   "api_key": "4c877630ce1fd306bb061697b2df107b019479d69d93e2cdb60efca53cc8b8c5"
# }
#
# search = GoogleSearch(params)
# results = search.get_dict()
# featured_prices = results["featured_prices"]
# print(results)
#
# print("-----------------------------------------------------------")
#
# for item in results:
#     print(item)
#
# print(results["total_rate"])



from serpapi import GoogleSearch

params = {
  "q": "jüSTa Sajjangarh Resort & Spa",
  "engine": "google_images",
  "ijn": "0",
  "api_key": "4c877630ce1fd306bb061697b2df107b019479d69d93e2cdb60efca53cc8b8c5"
}

search = GoogleSearch(params)
results = search.get_dict()
images_results = results["images_results"]
for image in images_results:
  # print(image["thumbnail"])
  print(image["original"])
  print("-----------------------------------")

