// WorldOfBeerMap


$(document).ready(function() {
    var map = new WorldOfBeerMap();
    map.createMap("mapCanvas");
});

// --------------------------------------------------------------------
// This bit is so freakin ugly, but is the only way I can find
// to stop the browser history being lost in firefox (3.6.13) 
// Somehow, while we are in the Geocoder callback, changes to 
// the location are not being saved in the browser history,
// so I just set the global selectedCountry variable there and
// poll it from this timer function until it is set and change
// location out here.
var selectedCountry = null;
function getMeOutOfHere(latLng)
{
    if (getMeOutOfHere.uglyTimer) {
        clearTimeout(getMeOutOfHere.uglyTimer);
        getMeOutOfHere.uglyTimer = null;
    }
    if (selectedCountry) {
        window.location = selectedCountry;
        return;
    }
    if (latLng != getMeOutOfHere.latLng) {
        getMeOutOfHere.attempt = 0;
        getMeOutOfHere.latLng  = latLng;
    }
    if (getMeOutOfHere.attempt < 5) {
        ++getMeOutOfHere.attempt;
        getMeOutOfHere.uglyTimer = setTimeout("getMeOutOfHere("+latLng+");", 100);
    }
}
// --------------------------------------------------------------------

function WorldOfBeerMap()
{
    this.geocoder = new google.maps.Geocoder();

    this.createMap = function(mapId)
    {
        // TODO change this cookie stuff to be saved per user
        var mapZoom = 2;
        var mapCentre = new google.maps.LatLng(-2.5, 152);
        var zoomlatlng = this.loadCookie();
        if (zoomlatlng) {
            mapZoom = parseInt(zoomlatlng[0]);
            mapCentre = new google.maps.LatLng(zoomlatlng[1], zoomlatlng[2]);
        }

        var wobMapOpts = { zoom: mapZoom,
                           center: mapCentre,
                           backgroundColor: "#3e487b",
                           disableDoubleClickZoom: true,
                           navigationControlOptions: {
                               style: google.maps.NavigationControlStyle.DEFAULT,
                               position: google.maps.ControlPosition.TOP_RIGHT },
                           mapTypeControlOptions: {
                               style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
                               mapTypeIds: [ 'WorldOfBeer',
                                             google.maps.MapTypeId.SATELLITE,
                                             google.maps.MapTypeId.TERRAIN ],
                               position: google.maps.ControlPosition.RIGHT_BOTTOM },
                           mapTypeId: 'WorldOfBeer',
                           streetViewControl: false };
        var map = new google.maps.Map(document.getElementById(mapId), wobMapOpts);
        var wobStyle = [ { featureType: "all",
                           elementType: "all",
                           stylers: [ { visibility: "off" } ] },
                         { featureType: "administrative.country",
                           elementType: "all",
                           stylers: [ {visibility: "on" } ] },
                         { featureType: "administrative.locality",
                           elementType: "all",
                           stylers: [ { visibility: "on" },
                                      { lightness: 30 } ] },
                         { featureType: "water",
                           elementType: "all",
                           stylers: [ { visibility: "on" },
                                      { hue: "#3c467b" },
                                      { lightness: -33 },
                                      { saturation: -28 },
                                      { gamma: 0.67 }, ] },
                         { featureType: "road.arterial",
                           elementType: "geometry",
                           stylers: [ { lightness: 62 },
                                      { visibility: "simplified" } ] },
                         { featureType: "road.highway",
                           elementType: "all",
                           stylers: [ { lightness: 62 },
                                      { visibility: "simplified" } ] },
                         { featureType: "landscape.natural",
                           elementType: "all",
                           stylers: [ { visibility: "on" } ] }
                       ];

        var wobTypeOpts = { name: "World of Beer" };
        var wobMapType = new google.maps.StyledMapType(wobStyle, wobTypeOpts);
        map.mapTypes.set('WorldOfBeer', wobMapType);

        var self = this;
        google.maps.event.addListener(map, 'dblclick', function(event) {
            selectedCountry = null;
            self.discoverCountry(event.latLng, function(country) {
                if (country) {
                    if ($.browser.mozilla) {
                        // stop the browser history being lost in firefox (3.6.13) 
                        selectedCountry = country;
                    } else {
                        // window.location works ok on Chrome - other browsers untested
                        window.location = country;
                    }

                } else {
                    map.panTo(event.latLng);
                    map.setZoom(map.getZoom()+1);
                }
            });
            // start polling for selectedCountry to be set
            if ($.browser.mozilla) {
                getMeOutOfHere(event.latLng);
            }
        });
        // TODO change this cookie stuff to be saved per user
        google.maps.event.addListener(map, 'center_changed', function(event) {
            self.saveCookie(map);
        });
        google.maps.event.addListener(map, 'zoom_changed', function(event) {
            self.saveCookie(map);
        });
    }

    this.discoverCountry = function(latlng, callback) 
    {
        function countryFromResults(results, status) 
        {
            if (status == google.maps.GeocoderStatus.OK) {
                for (i in results[0].address_components) {
                    var component = results[0].address_components[i];
                    for (j in component.types) {
                        var type = component.types[j];
                        if (type == "country") {
                            var name = component.long_name;
                            name = name.replace(" (FYROM)", "");
                            name = name.toLowerCase().replace(/\s+/g, '-');
                            name = encodeURIComponent(name);
                            return name;
                        }
                    }
                }
            } else {
                var lat = latlng.lat();
                var lng = latlng.lng();
                if (lat > 16 && lat < 27 && lng > 91 && lng < 99) {
                    return "burma";
                } 
                if ((lat > 31 && lat < 32.4 && lng > 34.9 && lng < 35.5) ||
                    (lat > 31.2 && lat < 31.6 && lng > 34.2 && lng < 34.5)) {
                    return "palestine";
                } 
                //alert(status+lat+":"+lng);
            }
            return "";
        }

        this.geocoder.geocode({'latLng': latlng, 'language': 'en'}, 
                              function(results, status) {
                                  var country = countryFromResults(results, status);
                                  callback(country);
                              });
    }

    // TODO change this cookie stuff to be saved per user
    this.loadCookie = function() 
    {
        var zoomlatlng = null;
        var rememberWhere = jQuery.cookie('world-of-beer-map');
        if (rememberWhere) {
            var zoomlatlng = rememberWhere.split(',');
        }
        return zoomlatlng;
    }

    this.saveCookie = function(map) 
    {
        var lat = map.getCenter().lat();
        var lng = map.getCenter().lng();
        var zoom = map.getZoom();
        var value = zoom+','+lat+','+lng;
        jQuery.cookie('world-of-beer-map', value, {path:'/'});
    }
}

