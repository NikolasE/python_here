
# PYTHON HERE

This package contains a simple and small wrapper for some functions of the REST-Interface for the [Here-API](https://developer.here.com/). 
It only contains the functions and use cases that I needed (either for a small fun-project or at a hackathon).
The functions are meant as starting points to show how functions can be called to give you a better idea how the API works. 

The functions and architecture will change randomly :)

Here provides a [Here Web Interface](https://refclient.ext.here.com/) that is very useful to experiment with routing functions before writing code. 

### Supported functions:
- compute Route from multiple waypoints (without reordering)
- compute distance matrix
- Sequence Optimization (Travelling Salesman)
- Generate map for route
- public transport
- reverse geo-coding (also as batch processing)


#### Planned Functions:
- improve codequality and usability of raster-visualization


### Visualization:

There are some (unfinished) tools to visualize traveltime by public transport (see imgs/munich_public_transport_distance.png):
- download_distance_data.py: uses the API to query distances for tiles in a regular grid and stores them in a file.
- the web-site in visualization/raster_map is an adapted version of the telco-example and loads the data (through a rest-interface provided by rest_data_server.py) and shows the map with color-coded tiles. Code was tested for Munich and New York. 




#### Keys:
Please create a keys.py in python_here (next to here_types.py) that contains your personal keys, it should look like

app_id = "9QUQxxxxxxxxx"

app_code = "0FLZ9442xxxxxxxxx"

#### Installation
Only dependency is python-requests
