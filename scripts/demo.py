#! /usr/bin/python3


from python_here.here_types import CalculateRouteResponse, WayPointParameter
from python_here.here_connection import HereConnector

from python_here.demo_data import Capitals
from python_here.helpers import print_distance_matrix

from python_here.keys import app_code, app_id


hc = HereConnector(app_id, app_code)

def public_transport_demo():
    print("#######################")
    print("A to B with public transport")
    # waypoints = Capitals[:2]
    # crr = hc.get_public_transport_route(waypoints[0], waypoints[1])

    start = WayPointParameter(48.147640, 11.514487, 'Hirschgarten')
    end = WayPointParameter(48.122551, 11.633449, 'Ostpark')
    crr = hc.get_public_transport_route(start, end)

    assert isinstance(crr, CalculateRouteResponse)

    print("Number of routes: %i" % len(crr.routes))

    r = crr.get_route(0)
    print(r.summary.distance//1000)

    filename = '/tmp/public.jpg'
    hc.route_to_image(r, filename)
    print("Check visualization at %s" % filename)



    # maneuvers = r.get_all_maneuvers()
    # for i, msg in enumerate(maneuvers):
    #     print(str(i) + ': %s' % (msg.instruction))

    # print("    Route from %s: %i km" % (" to ".join([w.label for w in waypoints]), r.summary.distance//1000))
    print("")

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
    optimized_waypoints = hc.optimize_sequence(waypoints)

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

def water_demo():
    print("#######################")
    print("Check if location is above water")

    points = list()
    points.append(WayPointParameter(48.5542345,10.4016703, "Donau"))
    points.append(WayPointParameter(47.6209996,9.3615463, "Lake of Constance"))
    points.append(WayPointParameter(48.1372423, 11.5746992, "Marienplatz"))
    points.append(WayPointParameter(40.785596, -73.9637147, "Kennedy Reservoir"))
    points.append(WayPointParameter(40.796199, -73.9870207, "Hudson"))
    print(hc.is_water_multi(points))

    # points.append(WayPointParameter(41.116871, 10.9811473, "Med sea"))
    #
    # for w in points:
    #     print(w.label + " is wet: " + str(hc.is_water(w)))


if __name__ == "__main__":

    # water_demo()

    # public_transport_demo()
    # route_demo()
    # sequence_demo()  #sequence call has a daily limit of around 10 requests per app_id
    matrix_demo()
