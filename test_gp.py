"""Integration tests for the gp (Goal Paces) API."""

import datetime
import json
#import os
import gp
import unittest
#import tempfile

class TestGoalPace(unittest.TestCase):
    def setUp(self):
        #self.db_fd, gp.app.config["DATABASE"] = tempfile.mkstemp()
        gp.app.config["TESTING"] = True
        self.app = gp.app.test_client()
        #gp.init_db()

    def tearDown(self):
        pass
        #os.close(self.db_fd)
        #os.unlink(gp.app.config["DATABASE"])

    def test_get_time_from_seconds(self):
        """It should convert floating point seconds in to a time object."""
        time = gp._get_time_from_seconds(3600)
        self.assertEquals(datetime.time(1), time)

    def test_respods_with_time(self):
        response = self.app.get("/api/v1/paces?time=2:52:37")
        response = json.loads(response.data)
        self.assertTrue("time" in response)
        self.assertEqual("2:52:37", response["time"])

    def test_response_with_100m_pace(self):
        """It should respond with the 100m pace for the marathon."""
        response = self.app.get("/api/v1/paces?time=3:00:00")
        response = json.loads(response.data)
        self.assertTrue("hundred_pace" in response)
        self.assertEqual("00:25", response["hundred_pace"])

        # The formula for computing 100m pace: goal_pace / (42195 / 100)
        pace = datetime.datetime.strptime("03:00:00", "%H:%M:%S")
        pace_seconds = (pace.hour * 3600.0) + (pace.minute * 60.0) + pace.second
        hundred_pace = pace_seconds / gp.HUNDRED_METER_CONVERSION
        self.assertAlmostEqual(25.5954496978315, hundred_pace)

    def test_response_with_marathon_pace(self):
        """It should compute and respond with marathon pace."""
        response = self.app.get("/api/v1/paces?time=2:52:37")
        response = json.loads(response.data)
        self.assertTrue("marathon_pace" in response, "Pace should be in response.")
        self.assertEqual("06:34", response["marathon_pace"])

    def test_compute_marathon_pace(self):
        """It should correctly compute marathon pace from hundred pace."""
        pace = gp._compute_marathon_pace(27.0)
        self.assertEqual(434.43, pace)

    def test_compute_marathon_pace_per_k(self):
        """It should compute marathon pace in seconds per kilometer."""
        seconds_per_kilometer = gp._compute_pace_per_kilometer(30.0)
        self.assertEqual(300, seconds_per_kilometer)

    def test_response_with_ten_and_twenty_percent_slower(self):
        """It should compute a training pace that is 10% slower than marathon pace."""
        response = self.app.get("/api/v1/paces?time=2:52:37")
        self.assertTrue(200, response.status_code)
        response = json.loads(response.data)
        self.assertTrue("ten_percent" in response)
        ten_percent = response["ten_percent"]
        self.assertEqual("07:14", ten_percent)
        self.assertTrue("twenty_percent" in response)
        twenty_percent = response["twenty_percent"]
        self.assertEqual("07:53", twenty_percent)

