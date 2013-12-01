function initialize() {

  var destructableStuff = {}

  $("input:checkbox").each(function( index ) {
    this.checked = false;
  });

  var centerlatlng = new google.maps.LatLng(30.320000, -97.770000);
  var myOptions = {
    zoom: 11,
    center: centerlatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

  function handleOptionToggle(type){
    if($("#"+type).is(':checked')){

      $.getJSON( "http://192.168.0.13:5000/data/?&type=" + type, function( data ) {

        $.each( data, function( shape, shapeHash ) {
          if (shape == "polygon") {
            $.each( shapeHash, function( type, typeHash ){
              destructableStuff[type] = []
              $.each( typeHash["paths"], function( index, coordArray){
                var coords = []
                $.each( coordArray, function( index, coordSets){
                  var coordSet = []
                  $.each( coordSets, function( index, coordPair){
                    coordSet.push(new google.maps.LatLng(coordPair[0], coordPair[1]))
                  });
                  coords.push(coordSet)
                });
                var polygon = new google.maps.Polygon({
                  clickable: false,
                  goedesic: true,
                  strokeOpacity: 1.0,
                  strokeWeight: 1,
                  fillColor: typeHash["fillColor"],
                  fillOpacity: typeHash["fillOpacity"],
                  strokeColor: typeHash["strokeColor"],
                  paths: coords
                });
                polygon.setMap(map);
                destructableStuff[type].push(polygon);
              });
            });
          }
        });
      });
    }
    else{
      $.each( destructableStuff[type], function(index, shape){
        shape.setMap(null);
      })
    }
  }

  $.getJSON( "http://192.168.0.13:5000/options", function( data ) {
    $.each(data, function(type, color){
      $("#map_interface_options").append("<li>
        <input type='checkbox' id='"+type+"' class='map-options'>"+type+"
        <span class='color-box' style='background: "+color+";'></span>
      </li>");
    })
  }

  $( ".map-option" ).click(function() {
    handleOptionToggle( $(this).attr('id') )
  });
}