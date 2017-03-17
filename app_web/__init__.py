from flask import Flask, render_template, request
import requests



app = Flask(__name__)
# app.config.from_object("app.config")

API_URL = "http://127.0.0.1:9000/"


@app.route("/", methods=["GET", "POST"])
def index():
    waypoints = []
    iframesrc = [];
    address = ""
    origin = ""
    geo_dest = ""
    geo_org = ""
    print("HERE")
    if request.method == "POST":
        address = request.form["address"]
        origin = request.form["origin"]
        print(address)
        print(origin)
        resp = requests.post(API_URL, data={"address": address, "origin":origin})
        # print(resp.json())
        print(resp)
        data = resp.json()
        iframesrc = data["src"]
        waypoints = data["waypoints"]
        geo_dest = data["geo_dest"]
        geo_org = data["geo_org"]



    return render_template("index2.html", dest=geo_dest, org=geo_org, waypts=waypoints, src=iframesrc,  address=address, origin=origin)
