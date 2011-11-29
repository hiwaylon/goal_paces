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

        self.assertTrue("mile_paces" in response)
        mile_paces = response["mile_paces"]
        self.assertTrue("marathon_pace" in mile_paces, "Pace should be in response.")
        self.assertEqual("06:34", mile_paces["marathon_pace"])

        self.assertTrue("kilometer_paces" in response)
        kilometer_paces = response["kilometer_paces"]
        self.assertTrue("marathon_pace" in kilometer_paces, "Pace should be in response.")
        self.assertEqual("04:05", kilometer_paces["marathon_pace"])


    def test_response_with_ten_and_twenty_percent_slower(self):
        """It should compute a training pace that is 10% slower than marathon pace."""
        response = self.app.get("/api/v1/paces?time=2:52:37")
        self.assertTrue(200, response.status_code)

        response = json.loads(response.data)
        self.assertTrue("fundamental" in response["mile_paces"])
        fundamentals = response["mile_paces"]["fundamental"]
        self.assertTrue("ten_percent" in fundamentals)
        ten_percent = fundamentals["ten_percent"]
        self.assertEqual("07:14", ten_percent)

        self.assertTrue("twenty_percent" in fundamentals)
        twenty_percent = fundamentals["twenty_percent"]
        self.assertEqual("07:53", twenty_percent)

        self.assertTrue("fundamental" in response["kilometer_paces"])
        fundamentals = response["kilometer_paces"]["fundamental"]
        self.assertTrue("ten_percent" in fundamentals)
        ten_percent = fundamentals["ten_percent"]
        self.assertEqual("04:30", ten_percent)

        self.assertTrue("twenty_percent" in fundamentals)
        twenty_percent = fundamentals["twenty_percent"]
        self.assertEqual("04:54", twenty_percent)
        
    def test_special_training_paces(self):
        """It should compute special training paces correctly."""
        response = self.app.get("/api/v1/paces?time=2:54:59")
        self.assertEqual(200, response.status_code)

        # km
        response = json.loads(response.data)
        self.assertTrue("special" in response["kilometer_paces"])
        special_ks = response["kilometer_paces"]["special"]
        self.assertEqual("03:49", special_ks["one_k"])
        self.assertEqual("03:56", special_ks["two_k"])
        self.assertEqual("04:00", special_ks["three_k"])
        self.assertEqual("04:02", special_ks["five_k"])
        self.assertEqual("04:11", special_ks["twenty_k"])
        self.assertEqual("04:38", special_ks["forty_five_k"])

        # mi
        self.assertTrue("special" in response["mile_paces"])
        special_ks = response["mile_paces"]["special"]
        self.assertEqual("06:09", special_ks["one_k"])
        self.assertEqual("06:20", special_ks["two_k"])
        self.assertEqual("06:26", special_ks["three_k"])
        self.assertEqual("06:30", special_ks["five_k"])
        self.assertEqual("06:44", special_ks["twenty_k"])
        self.assertEqual("07:28", special_ks["forty_five_k"])

    def test_specific_interval_paces(self):
        """It should create specific interval paces."""
        response = self.app.get("/api/v1/paces?time=2:54:59")
        response = json.loads(response.data)
        
        # km
        self.assertTrue("specific" in response["kilometer_paces"])
        self.assertTrue(
            "intervals" in response["kilometer_paces"]["specific"])
        specific_intervals_ks = \
            response["kilometer_paces"]["specific"]["intervals"]
        self.assertEqual("04:38", specific_intervals_ks["one_k"])
        self.assertEqual("04:03", specific_intervals_ks["four_k"])
        self.assertEqual("04:05", specific_intervals_ks["five_k"])
        self.assertEqual("04:06", specific_intervals_ks["six_k"])
        self.assertEqual("04:10", specific_intervals_ks["seven_k"])
        self.assertEqual("03:57", specific_intervals_ks["two_k"])
        self.assertEqual("04:31", specific_intervals_ks["thirty_five_k"])

        continuous_ks = \
            response["kilometer_paces"]["specific"]["continuous"]
        self.assertEqual("04:03", continuous_ks["twenty_five_k"])
        self.assertEqual("04:08", continuous_ks["thirty_k"])
        self.assertEqual("04:08", continuous_ks["thirty_k"])
        self.assertEqual("04:16", continuous_ks["thirty_five_k"])
        self.assertEqual("04:30", continuous_ks["forty_k"])

        # miles
        self.assertTrue("specific" in response["mile_paces"])
        self.assertTrue(
            "intervals" in response["mile_paces"]["specific"])
        interval_miles = \
            response["mile_paces"]["specific"]["intervals"]
        self.assertEqual("07:27", interval_miles["one_k"])
        self.assertEqual("06:32", interval_miles["four_k"])
        self.assertEqual("06:34", interval_miles["five_k"])
        self.assertEqual("06:35", interval_miles["six_k"])
        self.assertEqual("06:43", interval_miles["seven_k"])
        self.assertEqual("06:21", interval_miles["two_k"])
        self.assertEqual("07:17", interval_miles["thirty_five_k"])

        continuous_miles = \
            response["mile_paces"]["specific"]["continuous"]
        self.assertEqual("06:32", continuous_miles["twenty_five_k"])
        self.assertEqual("06:40", continuous_miles["thirty_k"])
        self.assertEqual("06:52", continuous_miles["thirty_five_k"])
        self.assertEqual("07:15", continuous_miles["forty_k"])

    def test_error(self):
        """It should 400."""
        response = self.app.get("/api/v1/paces?glorb=slert")
        self.assertEqual(400, response.status_code)
