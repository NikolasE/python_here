#! /usr/env/python

from python_here.here_types import WayPointParameter


def print_distance_matrix(starts, destinations, matrix):
    topline = 'Distance (km)'
    top_len = len(topline)
    for p in destinations:
        assert isinstance(p, WayPointParameter)
        topline += '%15s' % p.label
    print(topline)
    for i, s in enumerate(starts):
        l = s.label + ((top_len - len(s.label)) * ' ')
        for j in range(len(destinations)):
            l += "%15i" % (matrix[i][j] // 1000)
        print(l)
    print("")


def sec_to_hour_min(secs):
    hours = secs // 3600
    minutes = (secs - hours*3600)//60
    return hours, minutes
