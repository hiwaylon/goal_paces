"""gp (Goal Paces) Flask application file.

Compute marathon goal paces.

"""

import datetime
import json
# import logging

import flask
from flask import Flask, request
app = Flask(__name__)

# TODO - Move to lib/ or some Flask config structure
HUNDRED_METER_CONVERSION = 42195.0 / 100.0
HUNDRED_TO_MARATHON = 16.09


def _get_time_from_seconds(time_seconds):
    hours = int(time_seconds / 3600.0)
    time_seconds = time_seconds - hours * 3600.0
    minutes = int(time_seconds / 60.0)
    time_seconds = time_seconds - minutes * 60.0
    seconds = int(time_seconds)
    return datetime.time(hours, minutes, seconds)


def _compute_pace_per_kilometer(hundred_pace_seconds):
    return hundred_pace_seconds * 10.0


def _compute_marathon_pace(hundred_pace_seconds):
    return hundred_pace_seconds * HUNDRED_TO_MARATHON


@app.route("/")
def hello_world():
    return "Hi. Try /api/v1/paces?time=6:28"


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
    kilometer_pace_seconds = _compute_pace_per_kilometer(hundred_pace_seconds)
    marathon_pace = _get_time_from_seconds(kilometer_pace_seconds)
    kilometer_paces = {}
    kilometer_paces["marathon_pace"] = marathon_pace.strftime("%M:%S")

    ten_percent_km_pace = kilometer_pace_seconds * 1.1
    ten_percent_km = _get_time_from_seconds(ten_percent_km_pace)
    kilometer_paces["ten_percent"] = ten_percent_km.strftime("%M:%S")

    twenty_percent_km_pace = kilometer_pace_seconds * 1.2
    twenty_percent_km = _get_time_from_seconds(twenty_percent_km_pace)
    kilometer_paces["twenty_percent"] = twenty_percent_km.strftime("%M:%S")

    response["kilometer_paces"] = kilometer_paces

    # Minutes per mile.
    marathon_pace = _compute_marathon_pace(hundred_pace_seconds)
    marathon_pace = _get_time_from_seconds(marathon_pace)
    mile_paces = {}
    mile_paces["marathon_pace"] = marathon_pace.strftime("%M:%S")

    ten_percent_mi_pace = ten_percent_km_pace * 1.609
    ten_percent_mi = _get_time_from_seconds(ten_percent_mi_pace)
    mile_paces["ten_percent"] = ten_percent_mi.strftime("%M:%S")

    twenty_percent_km_pace = twenty_percent_km_pace * 1.609
    twenty_percent_km = _get_time_from_seconds(twenty_percent_km_pace)
    mile_paces["twenty_percent"] = twenty_percent_km.strftime("%M:%S")

    response["mile_paces"] = mile_paces

    return json.dumps(response)

    if __name__ == "__main__":
        # TODO - configuration variable for debug
        app.run(debug=True)
