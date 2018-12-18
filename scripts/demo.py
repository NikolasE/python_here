#! /usr/env/python


from python_here.here_types import CalculateRouteResponse
from python_here.here_connection import HereConnector

from python_here.demo_data import Capitals
from python_here.helpers import print_distance_matrix

from python_here.keys import app_code, app_id


hc = HereConnector(app_id, app_code)


def route_demo():
    print("#######################")
    print("Routing for multiple waypoints")
    waypoints = Capitals[:5]  # [Capitals[0], Capitals[15], Capitals[3]]

    crr = hc.calc_route(waypoints)
    assert isinstance(crr, CalculateRouteResponse)

    r = crr.get_route(0)
    print("    Route from %s: %i km" % (" to ".join([w.label for w in waypoints]), r.summary.distance//1000))

    filename = '/tmp/route.jpg'
    hc.route_to_image(r, filename)
    print("Check visualization at %s" % filename)

    # print("Total distance: %i km" % ))
    # maneuvers = r.get_all_maneuvers()
    # for i, msg in enumerate(maneuvers):
    #     print(str(i) + ': %.3f' % (msg.length))
    print("")


def sequence_demo():
    print("#######################")
    print("Optimizing waypoint sequence")
    waypoints = Capitals[:5]
    optimized_waypoints = hc.find_sequence(waypoints)

    crr = hc.calc_route(optimized_waypoints)
    assert isinstance(crr, CalculateRouteResponse)

    r = crr.get_route(0)
    print("Optimized route: %i km", r.summary.distance//1000)
    # print("    Route from %s: %i km" % (" to ".join([w.label for w in waypoints]), r.summary.distance//1000))

    filename = "/tmp/route_optimized.jpg"
    hc.route_to_image(r, filename)
    print("Check visualization at %s" % filename)


def matrix_demo():
    print("#######################")
    print("Creating distance matrix")
    starts = Capitals[:3]  # not more than 15 start points allowed
    destinations = Capitals[-4:]

    max_km = 500
    mat = hc.get_distance_matrix(starts, destinations, max_dist_km=max_km)
    if mat:
        print("(-1 for distances above %i km)" % (max_km))
        print_distance_matrix(starts, destinations, mat)
    print("")


if __name__ == "__main__":
    route_demo()
    # sequence_demo()  #sequence call has a daily limit of around 10 requests per app_id
    matrix_demo()
