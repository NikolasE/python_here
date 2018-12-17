#! /usr/env/python

import random

from python_here.here_types import CalculateRouteResponse
from python_here.here_connection import HereConnector

from python_here.demo_data import Capitals
from python_here.helpers import print_distance_matrix

from python_here.keys import app_code, app_id

hc = HereConnector(app_id, app_code)

if False:
    crr = hc.calc_route([Capitals[0], Capitals[15], Capitals[3]])
    assert isinstance(crr, CalculateRouteResponse)

    r = crr.get_route(0)
    maneuvers = r.get_all_maneuvers()
    # print (r.summary)
    for i, msg in enumerate(maneuvers):
        print(str(i) + ': %.3f' % (msg.length))


if True:
    starts = Capitals[:3]
    destinations = Capitals[-4:]

    mat = hc.get_distance_matrix(starts, destinations)
    if mat:
        print_distance_matrix(starts, destinations, mat)

