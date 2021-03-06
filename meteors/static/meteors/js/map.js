createLayer = function(colour) {
    return new ol.layer.Vector({
        style: new ol.style.Style({
            image: new ol.style.Circle({
                radius: 4,
                opacity: 0.6,
                fill: new ol.style.Fill({color: colour}),
            }),
        }),
    });
}

createMeteorLayer = function(meteors) {
    var layer = createLayer('red');
    var source = new ol.source.Vector();
    console.log("Adding meteor data for all");

    for (var m in meteors) {
        meteor = meteors[m];

        for (var s in meteor.snapshots) {
            snapshot = meteor.snapshots[s];
            console.log(snapshot);
            source.addFeature(
                new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.transform([snapshot.longitude, snapshot.latitude], 'EPSG:4326', 'EPSG:3857')),
                    style: new ol.style.Style({
                        image: new ol.style.Circle({
                            radius: Math.exp(3 - (snapshot.magnitude / 5)),
                        }),
                    }),
                })
            );
        }
    }

    layer.setSource(source);
    return layer;
}

createStationLayer = function(stations) {
    var layer = createLayer('blue');
    var source = new ol.source.Vector();

    console.log("Adding stations");
    for (var s in stations) {
        station = stations[s];
        console.log(station);
        source.addFeature(
            new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.transform([station.longitude, station.latitude], 'EPSG:4326', 'EPSG:3857')),
                style: new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: 3,
                        opacity: 0.5,
                        fill: new ol.style.Fill({
                            color: 'green',
                        }),
                    }),
                }),
            })
        );
    }
    layer.setSource(source);
    return layer;
}

createBasicMap = function() {
    var map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM(),
            }),
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([17.2738, 48.3729]),
            zoom: 9,
        })
    });

    return map;
}

loadMeteors = function(map) {
    $.getJSON("/meteors/json")
        .done(function(meteors) {
            map.addLayer(createMeteorLayer(meteors));
        })
        .fail(function() {
            console.log("Could not get JSON data");
        });

    $.getJSON("/stations/json")
        .done(function(stations) {
            map.addLayer(createStationLayer(stations));
        })
        .fail(function() {
            console.log("Could not get JSON data");
        });
}

initMap = function() {
    map = createBasicMap();
    loadMeteors(map);
}

$(document).ready(initMap);
