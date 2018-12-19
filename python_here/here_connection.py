#! /usr/bin/python3

import requests
from copy import deepcopy
from python_here.here_types import CalculateRouteResponse, WayPointParameter, Route
from python_here.helpers import date_string
from datetime import datetime
import json
import pprint


class HereConnector:
    calc_route_url = "https://route.api.here.com/routing/7.2/calculateroute.json"
    matrix_url = "https://matrix.route.api.here.com/routing/7.2/calculatematrix.json"
    route_image_url = "https://image.maps.api.here.com/mia/1.6/route"
    sequence_url = "https://wse.cit.api.here.com/2/findsequence.json"
    reverse_geocode_url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json"
    multi_reverse_geocode_url = "https://reverse.geocoder.api.here.com/6.2/multi-reversegeocode.json"

    water_location_types = ['river', 'lake']

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

        app_data['routeAttributes'] = 'waypoints,summary,legs,shape'

        r = requests.get(HereConnector.calc_route_url, app_data)
        if r.status_code != 200:
            HereConnector.print_error(r)
            return None

        crr = CalculateRouteResponse(r.json())
        return crr

    def get_public_transport_route(self, start, end):
        assert isinstance(start, WayPointParameter)
        assert isinstance(end, WayPointParameter)
        app_data = deepcopy(self.app_data_dict)

        # TODO: walking or driving to closest station?
        app_data['mode'] = 'fastest;publicTransport'
        app_data['waypoint0'] = str(start)
        app_data['waypoint1'] = str(end)
        app_data['combineChange'] = 'true'
        app_data['departure'] = date_string(datetime(2018, 12, 18, 12, 00))
        app_data['alternatives'] = 5  # up to N alternatives

        r = requests.get(HereConnector.calc_route_url, app_data)

        if r.status_code != 200:
            HereConnector.print_error(r)
            return None

        crr = CalculateRouteResponse(r.json())
        return crr

    def optimize_sequence(self, waypoints):
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
        # print("Number of legs: %i" % len(legs))
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
        app_data['m'] = way_point_str
        app_data['mlbl'] = 0 # numerical or alphanumerical numbering

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

        # TODO: check if iterable
        if not isinstance(destinations, list):
            destinations = [destinations]

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
        # print(response.json())
        try:
            print(response.json()['Details'])
            print(response.json()['AdditionalData'])
        except KeyError:
            print(response.json()['details'])
            print(response.json()['additionalData'])

    def is_water(self, waypoint, max_dist_m=0):
        # example for reverse geo lookup for single location        assert isinstance(waypoint, WayPointParameter)
        app_data = self.get_initial_appdata()
        app_data['prox'] = waypoint.geo_str()
        app_data['mode'] = 'retrieveLandmarks'

        r = requests.get(HereConnector.reverse_geocode_url, app_data)
        if r.status_code != 200:
            HereConnector.print_error(r)
            print(r.json())

            return None

        views = r.json()['Response']['View']
        if not views:
            return False

        results = views[0]['Result']
        for r in results:
            if r['Distance'] > max_dist_m:
                continue
            loc_type = r['Location']['LocationType']
            if loc_type in ['river', 'lake']:
                return True

        return False


    def is_water_multi(self, waypoints, max_dist_m=0):
        # example for multi-request reverse geocoding
        # https://developer.here.com/documentation/geocoder/topics/resource-multi-reverse-geocode.html

        app_data = self.get_initial_appdata()
        app_data['mode'] = 'retrieveLandmarks'
        app_data['maxresults'] = 5

        headers = {'Content-Type': 'application/xml; charset=utf8'}

        data = str()
        for w in waypoints:
            assert isinstance(w, WayPointParameter)
            data += "prox=%s\n" % (w.geo_str())

        r = requests.post(HereConnector.multi_reverse_geocode_url,
                          headers=headers,
                          params=app_data,
                          data=data  # "id=0023&prox=52.5309,13.3845,200"  # radius is ignored??
                          )

        if r.status_code != 200:
            HereConnector.print_error(r)
            print(r.json())
            return None

        is_water_list = list()

        pp = pprint.PrettyPrinter(indent=1)
        # pp.pprint(r.json())
        items = r.json()['Response']['Item']
        for item in items:
            # pp.pprint(item)

            is_water = 0

            # print(len(item['Result']))
            for r in item['Result']:
                dist = r['Distance']
                # negative distance if point is within polygon

                if dist > max_dist_m:
                    continue
                location_type = r['Location']['LocationType']
                if location_type in self.water_location_types:
                    is_water = -(self.water_location_types.index(location_type)+1)  # encode water type
                    # print("Dist to water: %f" % (dist))
                    # pp.pprint(r)
                    break

            is_water_list.append(is_water)
        return is_water_list
