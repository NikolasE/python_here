#! /usr/env/python

from python_here.here_types import WayPointParameter

major_cities = [
    ['Stuttgart', (48.7758459, 9.1829321)],
    ['Berlin', (52.520007, 13.404954)],
    ['Munich', (48.1367727, 11.5727545)],
    ['Postdam', (52.390569, 13.064473)],
    ['Bremen', (53.079296, 8.801694)],
    ['Hamburg', (53.551425, 9.994082)],
    ['Wiesbaden', (50.078218, 8.239761)],
    ['Schwerin', (53.628200, 11.415095)],
    ['Hannover', (52.373189, 9.738092)],
    ['Duesseldorf', (51.227741, 6.773456)],
    ['Mainz', (50.000126, 8.274035)],
    ['Saarbruecken', (49.233965, 6.994128)],
    ['Dresden', (51.050409, 13.737262)],
    ['Magdeburg', (52.127376, 11.637075)],
    ['Kiel', (54.323131, 10.140252)],
    ['Erfurt', (50.978075, 11.027302)]
]

Capitals = [WayPointParameter(e[1][0], e[1][1], e[0]) for e in major_cities]
