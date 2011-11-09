"""gp (Goal Paces) Flask application file.

Compute marathon goal paces.

"""

import datetime
import json
import logging

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

    # TODO - How to detect format errors here? strptime prolly throws something...
    time = datetime.datetime.strptime(request.args["time"], "%H:%M:%S")
    time_seconds = (time.hour * 3600.0) + (time.minute * 60.0) + time.second
    hundred_pace_seconds = time_seconds / HUNDRED_METER_CONVERSION
    marathon_pace_seconds = _compute_marathon_pace(hundred_pace_seconds)
   
    # NOTE - Do we care about rounding or microsecods?
    hundred_pace = _get_time_from_seconds(hundred_pace_seconds)
    marathon_pace = _get_time_from_seconds(marathon_pace_seconds)

    response = {
        "time": request.args["time"],
        "hundred_pace": hundred_pace.strftime("%M:%S"),
        "marathon_pace": marathon_pace.strftime("%M:%S"),
    }
    return json.dumps(response)

    if __name__ == "__main__":
        # TODO - configuration variable for debug
        app.run(debug=True)

