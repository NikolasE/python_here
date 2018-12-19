(function () {
'use strict';

var app_id = "DemoAppId01082013GAL";
var app_code = "AJKnXv84fjrb0KIHawS0Tg";
var host = "cit.datalens.api.here.com";


// Initialize communication with the platform, to access your own data, change the values below
// https://developer.here.com/documentation/geovisualization/topics/getting-credentials.html

// We recommend you use the CIT environment. Find more details on our platforms below
// https://developer.here.com/documentation/map-tile/common/request-cit-environment-rest.html

const platform = new H.service.Platform({
    app_id,
    app_code,
    useCIT: Boolean(host.match('cit')),  // map only works with CIT, otherwise CORS stops us
    useHTTPS: true
});

//initialize a map
const pixelRatio = devicePixelRatio > 1 ? 2 : 1;
const defaultLayers = platform.createDefaultLayers({tileSize: 256 * pixelRatio});
const map = new H.Map(
    document.getElementsByClassName('dl-map')[0],
    defaultLayers.normal.basenight,
    {pixelRatio}
);

window.addEventListener('resize', function() {
    map.getViewPort().resize();
});

//make the map interactive
new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
let ui = H.ui.UI.createDefault(map, defaultLayers);
ui.removeControl('mapsettings');

//instantiate Geovisualization service
const service = platform.configure(new H.datalens.Service());


// map.setCenter(new H.geo.Point(40.7589224,-73.9858918)); // new york
// map.setCenter(new H.geo.Point(48.13, 11.57)); // Munich
// map.setCenter(new H.geo.Point(50.3582024,7.5909793)); // Koblenz
map.setCenter(new H.geo.Point(52.5214172,13.4095033)); // Berlin
map.setZoom(14, false);

//https://developer.here.com/documentation/geovisualization/topics/quick-start.html
let provider = new H.datalens.RawDataProvider({
    /// we use a small flask-server to get the data (TODO: directly read local file
    dataUrl: 'http://0.0.0.0:8080/data',

    dataToFeatures: (data, helpers) => {
        // TODO: how can we read json instead of parsing a file?
        let parsed = helpers.parseCSV(data);
        let features = [];
        for (let i = 0; i < parsed.length; i++) {
            let row = parsed[i];
            if (i === 0)
            {
                this.lat_step = row[0];
                this.lng_step = row[1];
                continue;
            }
            if (i === 1)
            {
                // (How) can I access 'map' here?
                console.log(row[2]);
                if (row[2] === 'center') // TODO: deal with spaces
                {
                    this.center_lat = row[0];
                    this.center_lng = row[1];
                    console.log("Setting center");
                    // window.map.setCenter(row[0], row[1]);
                    continue;
                }
            }

            let feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [Number(row[1]), Number(row[0])]
                },
                "properties": {
                    "duration": Number(row[2])
                }
            };
            features.push(feature);
            // console.log(feature);
        }
        return features;
    },

    featuresToRows: (features, x, y, z, tileSize, helpers) => {
        let counts = {};
        let rows = [];

        let lat_step = this.lat_step;
        let lng_step = this.lng_step;

        for (let i = 0; i < features.length; i++) {
            let feature = features[i];

            let coordinates = feature.geometry.coordinates;
            let lng = coordinates[0];
            let lat = coordinates[1];

            let d = feature.properties.duration;
            // if (d < 0)
            {
                // console.log(d);
            }
            /// horrible data duplication, how can we pass lat_step once?
            rows.push({lat, lng, d, lat_step, lng_step});
        }
        return rows;
    }
});


const alpha = 0.5;
const COLORS = [
    'rgba(158, 1, 66, ' + alpha + ')',
    'rgba(238, 100, 69, ' + alpha + ')',
    'rgba(250, 177, 88, ' + alpha + ')',
    'rgba(243, 250, 173, ' + alpha + ')',
    'rgba(243, 250, 173, ' + alpha + ')',
    'rgba(199, 250, 173, ' + alpha + ')',
    'rgba(152, 213, 163, ' + alpha + ')',
    'rgba(92, 183, 169, ' + alpha + ')'
];


let max_dist = 1000; //  50*60;

// Using quantile scales, since domain is not a linear scale,
// but still need to snap value within these domain ranges.
// let colorScale = d3.scaleQuantile()
//     .domain([0, max_dist])
//     .range(COLORS);


// TODO: There has to be an easier way...
const colorScale = d3.scaleLinear().range(COLORS).domain(
    [0,
        1*max_dist/8,
        2*max_dist/8,
        3*max_dist/8,
        4*max_dist/8,
        5*max_dist/8,
        6*max_dist/8,
        7*max_dist/8,
        1]);

let layer = new H.datalens.ObjectLayer(
    provider,
    {
        pixelRatio,

        dataToRows: function(data) {
            return data;//.rows;
        },

        // takes row and returns polygon
        rowToMapObject: function(row) {
            let lat = row.lat;
            let lng = row.lng;

            // alpha=f=1 for accurate look
            // alpha=0.2, f=2 for strong blur
            let f = 1;

            let top = lat + row.lat_step/2.0*f;
            let bot = lat - row.lat_step/2.0*f;
            let left = lng - row.lng_step/2.0*f;
            let right = lng + row.lng_step/2.0*f;
            let strip = new H.geo.Strip([
                top, left, 0,
                top, right, 0,
                bot, right, 0,
                bot, left, 0
            ]);

            return new H.map.Polygon(strip);
        },

        rowToStyle: function(row) {
            let val = row.d;

            // console.log(row.d);


            // -1: no route found (but also river...
            if (val > max_dist) // || val < 0)
                val = max_dist;

            // let color = valueScale(val);
            let color = colorScale(val);

            if (val < 0)
            {
                color = 'rgba(255, 100, 130, 1)'; // ' + alpha + ')'
            }

            // if (val === -2) // lake
            // {
            //    color = 'rgba(0, 0, 255, ' + alpha + ')'
            // }
            //
            // if (val === -1) // river
            // {
            //     color = 'rgba(0, 100, 100, ' + alpha + ')'
            // }

            return {
                style: {
                    fillColor: color,
                    lineWidth: 0
                }
            };
        }
    }
);




//add layer on map
map.addLayer(layer);

// //init legend panel
// let panel = new Panel('Colormap');
// ui.addControl('panel', panel);
//
// const slider = new Slider(10);


// let selectLabel = new Label();
// let select = new Select([1, 2, 3, 4, 5].reduce(
//     (values, v) => {
//         values[v] = `Provider ${v}`;
//         return values;
//     }, {}
// ));
// panel.addChild(selectLabel);
// panel.addChild(slider);

// selectLabel.setHTML('provider');
// panel.addChild(select);

// let colorLegendLabel = new Label();
// let colorLegend = new ColorLegend(valueScale.copy().domain([0, 1]));
// panel.addChild(colorLegendLabel);
// panel.addChild(colorLegend);
// colorLegendLabel.setHTML('signal strength');
// colorLegend.setLabels(
//     [valueScale.domain()[0], valueScale.domain().slice(-1)]
// );
//
// select.addEventListener('change', () => {
//     provider.setQueryParams({provider_filter: select.getValue()});
//     provider.reload();
// });

}());

// function perc2color(perc) {
//     var r, g, b = 0;
//     if(perc < 50) {
//         r = 255;
//         g = Math.round(5.1 * perc);
//     }
//     else {
//         g = 255;
//         r = Math.round(510 - 5.10 * perc);
//     }
//     var h = r * 0x10000 + g * 0x100 + b * 0x1;
//     return '#' + ('000000' + h.toString(16)).slice(-6);
// }

