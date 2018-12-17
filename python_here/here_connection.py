#! /usr/env/python
import requests
from copy import deepcopy
from python_here.here_types import CalculateRouteResponse, WayPointParameter


class HereConnector:
    calc_route_url = "https://route.api.here.com/routing/7.2/calculateroute.json"
    matrix_url = "https://matrix.route.api.here.com/routing/7.2/calculatematrix.json"

    def __init__(self, app_id, app_code):
        self.mode = 'fastest;car;traffic:disabled'
        self.app_data_dict = {"app_id": app_id, "app_code": app_code}

    def get_initial_appdata(self):
        app_data = deepcopy(self.app_data_dict)
        app_data['mode'] = 'fastest;car;traffic:disabled'
        return app_data

    def calc_route(self, waypoints):
        # https://developer.here.com/documentation/routing/topics/resource-type-calculate-route.html
        app_data = self.get_initial_appdata()
        for i, p in enumerate(waypoints):
            assert isinstance(p, WayPointParameter)
            app_data['waypoint' + str(i)] = str(p)

        r = requests.get(HereConnector.calc_route_url, app_data)
        if r.status_code != 200:
            HereConnector.print_error(r)
            return None

        crr = CalculateRouteResponse(r.json())
        return crr

    # https://developer.here.com/documentation/routing/topics/resource-calculate-matrix.html
    def get_distance_matrix(self, starts, destinations, max_dist_km=-1):
        app_data = self.get_initial_appdata()
        app_data['summaryAttributes'] = 'distance'  # 'distance, costfactor, traveltime'

        for i, p in enumerate(starts):
            assert isinstance(p, WayPointParameter)
            app_data['start' + str(i)] = str(p)

        for i, p in enumerate(destinations):
            assert isinstance(p, WayPointParameter)
            app_data['destination' + str(i)] = str(p)

        if max_dist_km > 0:
            app_data['searchRange'] = max_dist_km * 1000

        r = requests.get(HereConnector.matrix_url, app_data)
        if r.status_code != 200:
            HereConnector.print_error(r)
            return None

        dist_mat = list()
        for i in range(len(starts)):
            dist_mat.append([-1] * len(destinations))

        j = r.json()

        mat = j['response']['matrixEntry']
        for e in mat:

            # catch distances above searchRange
            try:
                status = e['status']
                if status == 'rangeExceeded':
                    val = -1
                else:
                    print("Unhandled status exception: %s" % status)
                    val = -1
            except KeyError:
                summary = e['summary']
                val = summary['distance']
            dist_mat[e['startIndex']][e['destinationIndex']] = val

        return dist_mat

    @staticmethod
    def print_error(response):
        print(response.json()['details'])
        print(response.json()['additionalData'])
