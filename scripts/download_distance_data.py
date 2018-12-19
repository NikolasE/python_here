#! /usr/bin/python3

from python_here.here_connection import HereConnector
from python_here.here_types import Route, WayPointParameter
from math import sqrt
from geopy.distance import geodesic
from math import ceil
import time
import os

from python_here.keys import app_code, app_id
from python_here.helpers import print_distance_matrix
hc = HereConnector(app_id, app_code)


# Update these parameters
# destination = WayPointParameter(48.1372423,11.5746992, 'Marienplatz')
# top_left = (48.2258086,11.4096743)   # large area
# lower_right = (48.0555566,11.7890103)

destination = WayPointParameter(52.5214172,13.4095033, 'Alexanderplatz')
top_left = (52.5875622,13.2922933)
lower_right = (52.4680218,13.5129421)

# new york:
# destination = WayPointParameter(40.7589224,-73.9858918, 'Time Square')
# top_left = (40.860411,-74.0278517)
# lower_right = (40.693396,-73.8981547)


# Koblenz
# destination = WayPointParameter(50.3582024,7.5909793, 'Koblenz')
# top_left = (50.4089784,7.4756313)
# lower_right = (50.3110964,7.6673283)

# Magazino
# destination = WayPointParameter(48.1425936,11.5094533, 'Magazino')
# top_left = (48.1924986,11.4270753)
# lower_right = (48.1011766,11.6423343)

with_water_check = False
tile_count = 10000  # total number of points
filename = "berlin_10000_pub.txt"

if os.path.exists(filename):
    print("'%s' already exists, please remove or select other filename" % (filename))
    exit(1)

min_lat = lower_right[0]
lat_range = top_left[0]-min_lat

min_lng = top_left[1]
lng_range = lower_right[1] - min_lng

assert(lat_range > 0 and lng_range > 0)


# We need metric distances to get square tiles as longitude and latitude have different scaling
d_lat = geodesic((min_lat, min_lng), (min_lat+lat_range, min_lng)).meters
d_lng = geodesic((min_lat, min_lng), (min_lat, min_lng-lng_range)).meters


# Get size of tiles in geo-coordinates
cnt_lat = sqrt(d_lat * 1.0 / d_lng * tile_count)
cnt_lng = tile_count * 1.0 / cnt_lat

metric_resolution = d_lat/cnt_lat
print("Metric resolution: %.1f m" % (metric_resolution))


lat_step = lat_range/cnt_lat
lng_step = lng_range/cnt_lng

cnt_lat = ceil(cnt_lat)
cnt_lng = ceil(cnt_lng)

starts = list()
for la in range(cnt_lat):
    for ln in range(cnt_lng):
        lat = min_lat + la*lat_step
        lng = min_lng + ln*lng_step
        starts.append(WayPointParameter(lat, lng, "%i,%i" % (la, ln)))

outfile = open(filename, 'w')
outfile.write("%f, %f, 0\n" % (lat_step, lng_step))  # add scaling for visualization
outfile.write("%s,center\n" % (destination.geo_str()))  # add scaling for visualization


t1 = time.time()
num_starts = len(starts)

# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

num_water = 0

# using distance matrix is around 20 times faster, but does not support public transport
if False:
    cnt = 0
    for c in chunks(starts, 100):

        if with_water_check:
            water_type = hc.is_water_multi(c, max_dist_m=0)  # metric_resolution / 4)
            num_water += sum([1 for x in water_type if abs(x) > 0])

        # TODO: don't compute distance for positions in water
        dist_mat = hc.get_distance_matrix(c, destination)
        for i, w in enumerate(c):
            if with_water_check and (water_type[i]):
                outfile.write("%s,%i\n" % (w.geo_str(), water_type[i]))
            else:
                d = dist_mat[i][0]  # TODO: better flags
                if d < 0:  # no route found
                    d = -3
                outfile.write("%s,%f\n" % (w.geo_str(), d))

        cnt += len(c)
        secs_per_tile = (time.time() - t1) / cnt
        print("tiles/second: %.1f" % (1/secs_per_tile))
        remaining_time = (num_starts-cnt)*secs_per_tile
        print("%i / %i" % (cnt + 1, len(starts)))
        print("Remaining time: %.2f min" % (remaining_time/60))

    print("Found %i water cells" % (num_water))

if True:
    for i, w in enumerate(starts):
        if with_water_check and hc.is_water(w):
                min_dist = -2
                print('is water')
                num_water += 1
        else:
            # crr = hc.get_public_transport_route(w, destination)
            crr = hc.calc_route([w, destination])

            if crr:
                min_dist = min([r.summary.data['baseTime'] for r in crr.routes])
            else:
                print("no route found")
                min_dist = -3

        outfile.write(w.geo_str() + "," + str(min_dist) + '\n')

        if i > 0 and i%10 == 0:
            secs_per_tile = (time.time()-t1)/i
            print("tiles/second: %.1f" % (1/secs_per_tile))
            remaining_time = (num_starts-i)*secs_per_tile
            print("%i / %i" % (i + 1, len(starts)))
            print("Remaining time: %.2f min" % (remaining_time/60))

outfile.close()
print("Finished with %i tiles (%i water), stored to %s in %.2f minutes" %
      (num_starts, num_water, filename, (time.time()-t1)/60))