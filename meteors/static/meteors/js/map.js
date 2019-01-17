createMap = function() {
    var markerVectorLayer = new ol.layer.Vector({
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

    var map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM(),
            }),
            markerVectorLayer,
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([37.41, 8.82]),
            zoom: 4,
        })
    });

    var marker = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.transform([17.071388, 48.1501917], 'EPSG:4326', 'EPSG:3857')),
    });

    var style = 
    $.getJSON("/meteors/json").done(function(meteors) {
        var markers = [];
        for (var m in meteors) {
            meteor = meteors[m];
            console.log(meteor);
            markerVectorLayer.getSource().addFeature(
                new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.transform([meteor.longitude, meteor.latitude], 'EPSG:4326', 'EPSG:3857')),
                    style: new ol.style.Style({
                        image: new ol.style.Circle({
                            radius: 10,
                        }),
                    }),
                })
            );
        }

    }).fail(function() {
        console.log("Could not get JSON data");
    });

}

$(document).ready(createMap);
