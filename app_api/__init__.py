from flask import Flask, jsonify, request
from .api_funcs import parkGoog


app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    print('Start API')
    address = request.form["address"]
    print(address)
    origin = request.form["origin"]
    print(origin)
    org, dest, waypoints, src = parkGoog(origin, address)
    data = {
        "address": address,
        "src": src,
        "origin": origin,
        "waypoints": waypoints,
        "geo_org": org,
        "geo_dest": dest
    }
    print('\n\n')
    print(data['waypoints'])
    return jsonify(data)
