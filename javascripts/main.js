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

  function handleOptionToggle(type, app){
    if($("input[data-type='" + type +"']").is(':checked')){

      $.getJSON( "data/?&type=" + type + "&app=" + app, function( data ) {

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
                destructableStuff[app][type].push(polygon);
              });
            });
          }
        });
      });
    }
    else{
      $.each( destructableStuff[app][type], function(index, shape){
        shape.setMap(null);
      })
    }
  }

  function handleAppToggle(type){
    if($("input[data-type='" + type +"']").is(':checked')){

      $.getJSON( "app/?&type=" + type, function( data ) {
        $.each(data, function(type, color){
          $("#"+type+"_app_list").append("<li>\
            <span class='color-box' style='background: "+color+";'></span>\
            <input type='checkbox' data-type='"+type+"' class='map-option-"+type+"'>"+type+"\
          </li>");
        });

        $( ".map-option-"+type ).click(function() {
          handleOptionToggle( $(this).data('type'), type )
        });
      });
    }
    else{
      $.each( destructableStuff[type], function(index, option){
        $.each( destructableStuff[type][option], function(index, shape){
          shape.setMap(null);
        })
      })
    }
  }

  $.getJSON("apps/", function( data ) {
    $.each(data, function(type, color){
      $("#map_interface_apps").append("<li>\
        <input type='checkbox' data-type='"+type+"' class='map-option'>"+type+"\
        <ul id='"+type+"_app_list' class='app-option options'></ul>\
      </li>");
    });

    $( ".app-option" ).click(function() {
      handleAppToggle( $(this).data('type') )
    });
  });
}
