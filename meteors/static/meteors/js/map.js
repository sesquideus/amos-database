createMap = function() {

    var map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM(),
            }),
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([17.071388, 48.15091917]),
            zoom: 4,
        })
    });

    var marker = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.transform([17.071388, 48.1501917], 'EPSG:4326', 'EPSG:3857')),
    });


    $.getJSON("/meteors/json").done(function(meteors) {
        var meteorLayer = new ol.layer.Vector({
            source: new ol.source.Vector(),
            style: new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 6,
                    fill: new ol.style.Fill({color: 'red'}),
                    stroke: new ol.style.Stroke({
                        color: [255, 0, 0],
                        width: 2
                    }),
                }),
            }),
        });
        map.addLayer(meteorLayer);

        var markers = [];
        for (var m in meteors) {
            meteor = meteors[m];
            console.log(meteor);
            meteorLayer.getSource().addFeature(
                new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.transform([meteor.longitude, meteor.latitude], 'EPSG:4326', 'EPSG:3857')),
                    style: new ol.style.Style({
                        image: new ol.style.Circle({
                            radius: 5 - meteor.magnitude,
                        }),
                    }),
                })
            );
        }
    }).fail(function() {
        console.log("Could not get JSON data");
    });
/*
    var layer = createStationsLayer();
    if (layer !== null) {
        map.addLayer(layer);
    } else {
        throw "Could not load stations layer";
    } */

    $.getJSON("/stations/json").done(function(stations) {
        var stationLayer = new ol.layer.Vector({
            source: new ol.source.Vector(),
            style: new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 6,
                    fill: new ol.style.Fill({color: 'blue'}),
                    stroke: new ol.style.Stroke({
                        color: [0, 255, 0],
                        width: 2
                    }),
                }),
            }),
        });

        var markers = [];
        for (var s in stations) {
            station = stations[s];
            console.log(station);
            stationLayer.getSource().addFeature(
                new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.transform([station.longitude, station.latitude], 'EPSG:4326', 'EPSG:3857')),
                    style: new ol.style.Style({
                        image: new ol.style.Circle({
                            radius: 5,
                        }),
                    }),
                })
            );
        }
        map.addLayer(stationLayer);
    }).fail(function() {
        console.log("Could not get JSON data");
    });
}

initMap = function() {
    createMap();
}

$(document).ready(initMap);
