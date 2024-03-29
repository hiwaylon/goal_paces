"""gp (Goal Paces) Flask application file.

Compute marathon goal paces.

"""

import datetime
import json
import os

import flask
from flask import Flask, request, render_template
app = Flask(__name__)

HUNDRED_METER_CONVERSION = 42195.0 / 100.0
HUNDRED_TO_KM = 10.0
HUNDRED_TO_MARATHON = 16.09

def _get_time_from_seconds(time_seconds):
    hours = int(time_seconds / 3600.0)
    time_seconds = time_seconds - hours * 3600.0
    minutes = int(time_seconds / 60.0)
    time_seconds = time_seconds - minutes * 60.0
    seconds = int(time_seconds)
    return datetime.time(hours, minutes, seconds)


def _make_pace_time(multiplier, pace):
    seconds = multiplier * pace
    time = _get_time_from_seconds(seconds)
    return time.strftime("%M:%S")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/v1/paces")
def paces():
    if "time" not in request.args:
        # TODO - How do exception messages work in flask/werkzug?
        flask.abort(400)

    # Parse time from string.
    response = {}
    response["time"] = request.args["time"]
    # TODO - How to detect format errors here? strptime prolly throws
    # something...
    time = datetime.datetime.strptime(request.args["time"], "%H:%M:%S")

    # Convert to seconds.
    time_seconds = (time.hour * 3600.0) + (time.minute * 60.0) + time.second

    # Compute base paces.
    hundred_pace_seconds = time_seconds / HUNDRED_METER_CONVERSION
    hundred_pace = _get_time_from_seconds(hundred_pace_seconds)
    response["hundred_pace"] = hundred_pace.strftime("%M:%S")

    # Minutes per kilometer.
    kilometer_pace_seconds = hundred_pace_seconds * HUNDRED_TO_KM
    marathon_pace = _get_time_from_seconds(kilometer_pace_seconds)
    kilometer_paces = {}
    kilometer_paces["marathon_pace"] = marathon_pace.strftime("%M:%S")

    # Compute fundamental paces.
    fundamental = {}
    fundamental["ten_percent"] = _make_pace_time(1.1, kilometer_pace_seconds)
    fundamental["twenty_percent"] = _make_pace_time(
        1.2, kilometer_pace_seconds)
    kilometer_paces["fundamental"] = fundamental

    # Compute special paces.
    special = {}
    special["one_k"] = _make_pace_time(0.922, kilometer_pace_seconds)
    special["two_k"] = _make_pace_time(0.95, kilometer_pace_seconds)
    special["three_k"] = _make_pace_time(0.965, kilometer_pace_seconds)
    special["five_k"] = _make_pace_time(0.975, kilometer_pace_seconds)
    special["twenty_k"] = _make_pace_time(1.01, kilometer_pace_seconds)
    special["forty_five_k"] = _make_pace_time(1.12, kilometer_pace_seconds)
    kilometer_paces["special"] = special

    # Compute specific paces.
    intervals = {}
    intervals["one_k"] = _make_pace_time(1.12, kilometer_pace_seconds)
    intervals["four_k"] = _make_pace_time(0.98, kilometer_pace_seconds)
    intervals["five_k"] = _make_pace_time(0.986, kilometer_pace_seconds)
    intervals["six_k"] = _make_pace_time(0.989, kilometer_pace_seconds)
    intervals["seven_k"] = _make_pace_time(1.008, kilometer_pace_seconds)
    intervals["two_k"] = _make_pace_time(0.953, kilometer_pace_seconds)
    intervals["thirty_five_k"] = _make_pace_time(1.09, kilometer_pace_seconds)
    kilometer_paces["specific"] = {"intervals": intervals}

    continuous = {}
    continuous["twenty_five_k"] = _make_pace_time(
        0.980, kilometer_pace_seconds)
    continuous["thirty_k"] = _make_pace_time(1.0, kilometer_pace_seconds)
    continuous["thirty_five_k"] = _make_pace_time(
        1.031, kilometer_pace_seconds)
    continuous["forty_k"] = _make_pace_time(1.087, kilometer_pace_seconds)
    kilometer_paces["specific"]["continuous"] = continuous

    response["kilometer_paces"] = kilometer_paces

    # Minutes per mile.
    marathon_pace = hundred_pace_seconds * HUNDRED_TO_MARATHON
    marathon_pace = _get_time_from_seconds(marathon_pace)
    mile_paces = {}
    mile_paces["marathon_pace"] = marathon_pace.strftime("%M:%S")
    
    # Compute fundamental paces.
    fundamental = {}
    fundamental["ten_percent"] = _make_pace_time(
        1.1 * 1.609, kilometer_pace_seconds)
    fundamental["twenty_percent"] = _make_pace_time(
        1.2 * 1.609, kilometer_pace_seconds)
    mile_paces["fundamental"] = fundamental

    # Compute special paces.
    special = {}
    special["one_k"] = _make_pace_time(0.922 * 1.609, kilometer_pace_seconds)
    special["two_k"] = _make_pace_time(0.95 * 1.609, kilometer_pace_seconds)
    special["three_k"] = _make_pace_time(0.965 * 1.609, kilometer_pace_seconds)
    special["five_k"] = _make_pace_time(0.975 * 1.609, kilometer_pace_seconds)
    special["twenty_k"] = _make_pace_time(1.01 * 1.609, kilometer_pace_seconds)
    special["forty_five_k"] = _make_pace_time(1.12 * 1.609, kilometer_pace_seconds)
    mile_paces["special"] = special

    # Compute specific paces.
    intervals = {}
    intervals["one_k"] = _make_pace_time(1.117 * 1.609, kilometer_pace_seconds)
    intervals["four_k"] = _make_pace_time(0.98 * 1.609, kilometer_pace_seconds)
    intervals["five_k"] = _make_pace_time(0.986 * 1.609, kilometer_pace_seconds)
    intervals["six_k"] = _make_pace_time(0.989 * 1.609, kilometer_pace_seconds)
    intervals["seven_k"] = _make_pace_time(1.008 * 1.609, kilometer_pace_seconds)
    intervals["two_k"] = _make_pace_time(0.953 * 1.609, kilometer_pace_seconds)
    intervals["thirty_five_k"] = _make_pace_time(1.092896 * 1.609, kilometer_pace_seconds)
    mile_paces["specific"] = {"intervals": intervals}

    continuous = {}
    continuous["twenty_five_k"] = _make_pace_time(
        0.980 * 1.609, kilometer_pace_seconds)
    continuous["thirty_k"] = _make_pace_time(1.0 * 1.609, kilometer_pace_seconds)
    continuous["thirty_five_k"] = _make_pace_time(
        1.031 * 1.609, kilometer_pace_seconds)
    continuous["forty_k"] = _make_pace_time(1.087 * 1.609, kilometer_pace_seconds)
    mile_paces["specific"]["continuous"] = continuous
    response["mile_paces"] = mile_paces

    return json.dumps(response)

@app.route("/api/v1/race")
def race():
    if "distance" not in request.args:
        flask.abort(400)
    distance = float(request.args["distance"])
    if "time" not in request.args:
        flask.abort(400)
    try:
        time = datetime.datetime.strptime(request.args["time"], "%H:%M:%S")
    except ValueError:
        time = datetime.datetime.strptime(request.args["time"], "%M:%S")
    time_in_seconds = (time.hour * 3600.0) + (time.minute * 60.0) + time.second 
    mile_pace = time_in_seconds / distance
    mile_pace = _get_time_from_seconds(mile_pace)
    mile_pace = mile_pace.strftime("%M:%S")
    response = {"mile_pace": mile_pace}
    return json.dumps(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
