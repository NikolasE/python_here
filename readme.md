
# PYTHON HERE

This package contains a simple and small wrapper for the REST-Interface for the [Here-API](https://developer.here.com/). 
It only contains the functions and use cases that I needed (either for a small fun-project or at a hackahton). 

The functions and architecture will change randomly :)

### Supported functions:
- compute Route from multiple waypoints (without reordering)
- compute distance matrix
- Sequence Optimization (Travelling Salesman)
- Generate map for route


#### Planned Functions:
- public transport


#### Keys:
Please create a keys.py in python_here (next to here_types.py) that contains your personal keys, it should look like

app_id = "9QUQxxxxxxxxx"

app_code = "0FLZ9442xxxxxxxxx"

#### Installation
Only dependency is python-requests