#! /usr/env/python


class Names:
    # https://developer.here.com/documentation/routing/topics/resource-type-route.html
    def __init__(self):
        self.distance = "Distance"
        self.traffic_time = "TrafficTime"
        self.travel_time = "TravelTime"
        self.cost_factor = "CostFactor"
        self.all = [self.distance, self.traffic_time, self.cost_factor]


class Summary:
    # Summary almost completely consists of optional arguments, not yet implemented
    # https://developer.here.com/documentation/routing/topics/resource-type-route-summary.html
    def __init__(self, d):
        # print(d)
        self.data = d
        self.distance = d['distance']

    def has(self, info):
        assert isinstance(info, str)
        return info in self.data

    def get(self, info):
        assert isinstance(info, str)
        try:
            return self.data[info]
        except KeyError:
            return None

    def get_hours_minutes(self):
        # seconds = self.get(Names.)
        pass

    def __str__(self):
        return str(self.data)


class GeoCoordinate:
    def __init__(self, j):
        self.longitude = j['longitude']
        self.latitude = j['latitude']

    def __str__(self):
        return "%s,%s" % (self.latitude, self.longitude)


class WayPointParameter:
    # https://developer.here.com/documentation/routing/topics/resource-param-type-waypoint.html
    def __init__(self, lat, lng, label=''):
        self.latitude = lat
        self.longitude = lng
        self.label = label

    def __str__(self):
        s = "geo!%f,%f" % (self.latitude, self.longitude)
        if self.label:
            s += ';;'+self.label  # empty radius
        return s

    def geo_str(self):
        return "%s,%s" % (self.latitude, self.longitude)


class WayPoint:
    # https://developer.here.com/documentation/routing/topics/resource-type-waypoint.html
    def __init__(self, j):
        self.raw_data = j
        self.link_id = j['linkId']
        self.position = GeoCoordinate(j['mappedPosition'])
        try:
            self.original_position = GeoCoordinate(j['originalPosition'])
        except KeyError as e:
            print("Loading waypoint: " + str(e))
            pass


class Maneuver:
    def __init__(self, j):
        self.raw_data = j
        self.position = GeoCoordinate(j['position'])
        self.instruction = j['instruction']
        self.travel_time = j['travelTime']
        self.length = j['length']


class Leg:
    def __init__(self, j):
        self.raw_data = j
        self.start = WayPoint(j['start'])
        self.end = WayPoint(j['end'])
        self.length = j['length']
        self.travel_time = j['travelTime']
        self.maneuvers = [Maneuver(e) for e in j['maneuver']]


class Route:
    def __init__(self, j):
        # print(j.keys())
        self.summary = Summary(j['summary'])
        self.requested_waypoints = [WayPoint(e) for e in j['waypoint']]
        self.legs = [Leg(e) for e in j['leg']]

    def __str__(self):
        maneuver_cnt = sum([len(l.maneuvers) for l in self.legs])
        km = self.summary.distance//1000.0
        return "Route with %i legs with %i maneuvers and distance of %i km" % (len(self.legs), maneuver_cnt, km)

    def get_all_maneuvers(self):
        maneuvers = list()
        for l in self.legs:
            for m in l.maneuvers:
                maneuvers.append(m)
        return maneuvers


class CalculateRouteResponse:
        def __init__(self, j):
            r = j['response']
            self.meta_info = r['metaInfo']
            self.language = r['language']
            self.routes = [Route(e) for e in r['route']]

        def get_route(self, index=0):
            if index > len(self.routes):
                return None
            return self.routes[index]

        def print_info(self):
            print("RouteResponse with %i routes:" % (len(self.routes)))
            for i, r in enumerate(self.routes):
                print("  " + str(i) + ': ' + str(r))
