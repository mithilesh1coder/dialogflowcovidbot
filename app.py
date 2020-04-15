# flask_ngrok_example.py
from flask import Flask, request, make_response, jsonify
from flask_ngrok import run_with_ngrok
import requests
from geopy.geocoders import Nominatim
import smtplib
import os

app = Flask(__name__)
run_with_ngrok(app)  # Start ngrok when app is run


@app.route("/", methods=["GET"])
def home():
    return "Welcome to covid Bot"


@app.route("/webhook", methods=["POST"])
def webhook():
    # if request.get_json().get("queryResult").get("action") != "covidIntent":
    # return {}

    query_state = ""
    district_data = dict()
    concat_data = ""

    states = [
        "Andaman and Nicobar Islands",
        "Delhi",
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jammu and Kashmir",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Orissa",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telagana",
        "Tripura",
        "Uttaranchal",
        "Uttar Pradesh",
        "West Bengal",
    ]

    val = request.json
    user_name = val["queryResult"]["parameters"]["user_name"]
    user_email = val["queryResult"]["parameters"]["user_email"]
    user_mobile = val["queryResult"]["parameters"]["user_mobile"]
    user_pincode = val["queryResult"]["parameters"]["user_pincode"]

    print(user_pincode, user_name, user_mobile, user_email)

    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(user_pincode)

    add = location.address

    for state in states:
        if state in add:
            query_state = state

    data = requests.get(
        "https://api.covid19india.org/v2/state_district_wise.json"
    ).json()

    sum = 0

    for i in range(len(data)):
        if data[i]["state"].lower() == query_state.lower():
            district_data = data[i]["districtData"]
            for j in range(len(data[i]["districtData"])):

                # gather all distric data

                sum = sum + int(data[i]["districtData"][j]["confirmed"])

    print(sum)

    # Send mail
    s = smtplib.SMTP("smtp.gmail.com", 587)
    # start TLS for security
    s.starttls()

    # Authentication
    s.login("mithi.rocks123@gmail.com", os.environ["GMAIL_PASSWORD"])

    for k in district_data:
        dis = k["district"]
        conf = k["confirmed"]
        concat_data += dis + ":" + str(conf) + "\n"

    # message to be sent
    message = (
        "Hi "
        + user_name
        + ",Total number of cases for your state "
        + query_state
        + " is "
        + str(sum)
        + "\n"
        + concat_data
    )

    # sending the mail
    s.sendmail("mithi.rocks123@gmail.com", user_email, message)

    # terminating the session
    s.quit()

    final_res = (
        {"fulfillmentText": "Total cases in " + query_state + " is " + str(sum)}
        + "\nCovid 19 case details for your location has been sent to your mail id.Keep Indoors and be safe."
    )
    return make_response(jsonify(final_res))


if __name__ == "__main__":
    app.run()
