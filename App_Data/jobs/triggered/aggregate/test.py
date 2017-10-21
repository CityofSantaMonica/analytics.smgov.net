import job
import unittest

class JobTest(unittest.TestCase):
    # This function is the first layer of aggregation that's used for all the reports to merge up the 'totals' attributes
    # from each of the reports
    def test_sum_shared_dict_keys(self):
        objectOne = {
            "int": 10,
            "list": [1, 2, 3],
            "tuple": (10, 20),
            "dict": {
                "int": 2,
                "list": [1, 2]
            }
        }
        objectTwo = {
            "int": 5,
            "list": [4, 5, 6],
            "tuple": (20, 30),
            "dict": {
                "int": 8,
                "list": [9, 8]
            }
        }

        result = job.sum_shared_dict_keys(objectOne, objectTwo)
        self.assertEqual(result, {
            "int": 15,
            "list": [1, 2, 3, 4, 5, 6],
            "dict": {
                "int": 10,
                "list": [1, 2, 9, 8]
            }
        })

    # This function is the core for aggregating information from the following reports:
    #
    #   - 'all-pages-realtime.json'
    #   - 'today.json'
    #   - 'last-48-hours.json'
    #   - 'users.json'
    def test_sum_data_by_key_lambda(self):
        data = [
            { "country": "United States", "city": "Los Angeles", "page": "/rider-info/real-time-info.aspx",
              "page_title": "Real-Time Info - Big Blue Bus", "active_visitors": "2", "domain": "www.bigbluebus.com"
            }, {
              "country": "United States", "city": "Los Angeles", "page": "/routes-and-schedules/route-8.aspx",
              "page_title": "Route 8 - Ocean Park Blvd - Big Blue Bus", "active_visitors": "2", "domain": "www.bigbluebus.com"
            }, {
              "country": "United States", "city": "Indianapolis", "page": "/default.aspx", "page_title": "Big Blue Bus",
              "active_visitors": "1", "domain": "www.bigbluebus.com"
            }, {
              "country": "United States", "city": "Santa Monica", "page": "/default.aspx", "page_title": "Big Blue Bus",
              "active_visitors": "6", "domain": "www.bigbluebus.com"
            }, {
              "country": "United States", "city": "Los Angeles", "page": "/fares/fare-information.aspx",
              "page_title": "Fare Information - Big Blue Bus", "active_visitors": "1", "domain": "www.bigbluebus.com"
            }, {
              "country": "United States", "city": "Santa Monica", "page": "/fares/fare-information.aspx",
              "page_title": "Fare Information - Big Blue Bus", "active_visitors": "4", "domain": "www.bigbluebus.com"
            }, {
              "country": "United States", "city": "Los Angeles", "page": "/departments/pcd/transportation/motorists-parking/",
              "page_title": "Motorists Parking - Planning & Community Development - City of Santa Monica",
              "active_visitors": "2", "domain": "www.smgov.net"
            }, {
              "country": "United States", "city": "Los Angeles", "page": "/departments/pcd/transportation/motorists-parking/where-to-park/",
              "page_title": "Where to Park - Planning & Community Development - City of Santa Monica", "active_visitors": "2",
              "domain": "www.smgov.net"
            }, {
              "country": "United States", "city": "Los Angeles", "page": "/default.aspx", "page_title": "City of Santa Monica",
              "active_visitors": "2", "domain": "www.smgov.net"
            }, {
              "country": "United States", "city": "Santa Monica", "page": "/default.aspx", "page_title": "City of Santa Monica",
              "active_visitors": "6", "domain": "www.smgov.net"
            }
        ]

        # We're summing up the 'active_visitors' key
        result = job.sum_data_by_key(
            data,
            lambda x: x['domain'] + x['page'],
            'active_visitors',
            ['country', 'city']
        )

        # These should be the totals for the sample dataset
        expected_count = {
            "Real-Time Info - Big Blue Bus": 2,
            "Route 8 - Ocean Park Blvd - Big Blue Bus": 2,
            "Big Blue Bus": 7,
            "Fare Information - Big Blue Bus": 5,
            "Motorists Parking - Planning & Community Development - City of Santa Monica": 2,
            "Where to Park - Planning & Community Development - City of Santa Monica": 2,
            "City of Santa Monica": 8
        }

        for count in expected_count.items():
            for item in result:
                if item['page_title'] == count:
                    self.assertEqual(item['active_visitors'], expected_count[count])

    def test_sum_data_by_key_str(self):
        data = [
            { "visits": "5", "date": "2017-03-12", "hour": "01" },
            { "visits": "10", "date": "2017-03-12", "hour": "02" },
            { "visits": "10", "date": "2017-03-12", "hour": "03" },
            { "visits": "5", "date": "2017-03-12", "hour": "04" },

            { "visits": "50", "date": "2017-03-12", "hour": "01" },
            { "visits": "20", "date": "2017-03-12", "hour": "02" },
            { "visits": "20", "date": "2017-03-12", "hour": "03" },
            { "visits": "10", "date": "2017-03-12", "hour": "04" },
        ]

        result = job.sum_data_by_key(data, 'hour', 'visits')

        expected_count = {
            '01': 55,
            '02': 30,
            '03': 30,
            '04': 15,
        }

        for count in expected_count.items():
            for item in result:
                if item['hour'] == count:
                    self.assertEqual(item['visits'], expected_count[count])

if __name__ == '__main__':
    unittest.main()