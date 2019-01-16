$(document).ready(createMap);
console.log("fuck");

createMap = function() {
    console.log("fuck");
    map = new OpenLayers.Map("map");
    map.addLayer(new OpenLayers.Layer.OSM());

    var lonLat = new OpenLayers.LonLat({{ meteor.lightmaxLongitude }}, {{ meteor.lightmaxLatitude }})
          .transform(
            new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
            map.getProjectionObject() // to Spherical Mercator Projection
          );
          
    var zoom=10;

    var markers = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markers);

    markers.addMarker(new OpenLayers.Marker(lonLat));

    map.setCenter (lonLat, zoom);
}
