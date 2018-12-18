#! /usr/env/python
import requests
from copy import deepcopy
from python_here.here_types import CalculateRouteResponse, WayPointParameter, Route


class HereConnector:
    calc_route_url = "https://route.api.here.com/routing/7.2/calculateroute.json"
    matrix_url = "https://matrix.route.api.here.com/routing/7.2/calculatematrix.json"
    route_image_url = "https://image.maps.api.here.com/mia/1.6/route"
    sequence_url = "https://wse.cit.api.here.com/2/findsequence.json"


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

    def find_sequence(self, waypoints):
        app_data = self.get_initial_appdata()

        waypoint_count = len(waypoints)

        for i, w in enumerate(waypoints):
            assert isinstance(w, WayPointParameter)
            if i == 0:
                app_data['start'] = w.geo_str()
                continue

            if i == waypoint_count-1:
                app_data['end'] = w.geo_str()
                continue

            app_data['destination' + str(i)] = w.geo_str()

        r = requests.get(HereConnector.sequence_url, app_data)
        if r.status_code != 200:
            HereConnector.print_error(r)
            return None

        j = r.json()
        waypoints = j['results'][0]['waypoints']

        optimized_waypoints = list()

        for w in waypoints:
            wp = WayPointParameter(w['lat'], w['lng'])
            optimized_waypoints.append(wp)

        return optimized_waypoints

    def route_to_image(self, route, filename):
        # https://developer.here.com/documentation/map-image/topics/resource-route.html
        assert isinstance(route, Route)
        legs = route.legs
        print("Number of legs: %i" % len(legs))
        way_points = list()

        maneuvers = route.get_all_maneuvers()
        way_point_cnt = len(maneuvers)
        if way_point_cnt > 120:
            print("High number of maneuvers (%i), consider sampling" % (len(way_points)))

        way_point_str = ",".join([str(m.position) for m in maneuvers])

        app_data = self.get_initial_appdata()
        app_data['h'] = 1024
        app_data['w'] = 1024
        # app_data['ppi'] = 100  # resolution
        app_data['t'] = 3  # type (day, night, ...)

        app_data['lc'] = '990000ff'  # line color
        app_data['lw'] = 10          # line width

        app_data['r'] = way_point_str  # route waypoints, use r0, r1 for multiple routes

        # marker
        # app_data['m'] = way_point_str
        # app_data['mlbl'] = 0 # numerical or alphanumerical numbering

        # app_data['f'] = 0  # format 1/jpeg is default

        r = requests.get(HereConnector.route_image_url, app_data)
        # print(r.url)

        # print r.status_code
        f = open(filename, 'wb')
        f.write(r.content)
        f.close()

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
