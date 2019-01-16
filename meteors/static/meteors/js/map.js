createMap = function() {
    map = new OpenLayers.Map("map");
    map.addLayer(new OpenLayers.Layer.OSM());
    var zoom = 10;

    var markers = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(markers);

    $.getJSON("/meteors/json").done(function(meteors) {
        for (var m in meteors) {
            meteor = meteors[m];
            console.log(meteor);
            var coord = new OpenLayers.LonLat(meteor.longitude, meteor.latitude).transform(
                new OpenLayers.Projection("EPSG:4326"),
                map.getProjectionObject()
            );
            markers.addMarker(new OpenLayers.Marker(coord));
        }
    }).fail(function() {
        console.log("Could not get JSON data");
    });



    map.setCenter(new OpenLayers.LonLat(0, 0), zoom);
}

$(document).ready(createMap);
