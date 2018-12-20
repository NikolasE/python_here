#! /usr/bin/python3

# This is rather a Hack to get the csv file into the javascript-application
# TODO: accept filename as  get-parameter and provide list of possible files

from flask import Flask, Response, request

app = Flask(__name__)

filename = '../example_data/munich_public_large_square.txt'
content = open(filename).read()
response = Response(content, mimetype="text/html")
response.headers.add('Access-Control-Allow-Origin', '*')


@app.route('/data', methods=['GET', 'POST'])
def get_data():
    print(request.args)

    try:
        filename = request.args['file']
    except KeyError:
        filename = '../example_data/munich_public_large_square.txt'

    # filename = '../example_data/munich_public_large_square.txt'
    content = open(filename).read()
    response = Response(content, mimetype="text/html")
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == "__main__":
    example_url = "http://localhost:8080/data"
    print("Open this: %s" % example_url)
    app.run(host='0.0.0.0', port=8080, debug=True)




# f = open(filename, 'r')
# features = list()
# max_dist = -1
#
# for l in f.readlines():
#
#     try:
#         spl = list(map(float, l.split(',')))
#     except ValueError:
#         continue
#     max_dist = max(max_dist, spl[2])
#
#     # f = {"type": "Feature",
#     #      "geometry":
#     #          {"type":"Point",
#     #           'coordinates': [spl[0], spl[1]]},
#     #      'properties': {'distance': spl[2]/60.0}
#     #      }
#     features.append(f)
#
# print("Max dist: %i" % max_dist)
# f.close()
