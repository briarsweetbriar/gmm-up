
/*

Accepts a hash table of data (defined within 
this file and/or provided by calls to the urls 
./apps and ./data), and renders the geometry 
to a google map. 

*/
function initialize() {

  var destructableStuff = {}

  /*Master variable of all data within all of the apps

  has the following structure:
    data = {
     "AppName": {
       'dataset1': { 
	 'color': '#00FF00' //color to display on key
	 'title': 'Data Set #1'
         'markers': [
            { points to plot }, 
            {'lat':37.220,'lon':-96.904,'color': '#000000', 'title':'pt1'}, 
            {'lat':30.384,'lon': -97.683,'title':'pt2'}, //same color as last one
            {'lat':29.629,'lon': -98.492,'color':'#00FF00', 'title':'pt3'} //new color
         ],
        },
      }      
    }
    '''

  */
  var jsonData = {/* INSERT JSON DATA HERE */};  //Do not change this tag!

  $("input:checkbox").each(function( index ) {
    this.checked = false;
  });

  var centerlatlng = new google.maps.LatLng(30.320000, -97.770000);
  var myOptions = {
    zoom: 5,
    center: centerlatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

  function handleOptionToggle(type, app){
    if($("input[data-type='" + type +"']").is(':checked')){

      $.getJSON( "data/?&type=" + type + "&app=" + app, function( data ) {

        alert("todo: push this data into jsonData");
      })

      .always( function() {

        $.each( jsonData[app][type], function( shape, shapeHash ) {
           /*if (shape == "polygon") {
            $.each( shapeHash, function( type, typeHash ){
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
                if (!(app in destructableStuff)){
                  destructableStuff[app] = {}
                }
                if (!(type in destructableStuff[app])){
                  destructableStuff[app][type] = []
                }
                destructableStuff[app][type].push(polygon);
              });
            });
          }*/
           if (shape == "markers") {
              $.each( shapeHash, function(index,pointHash ){
                 var latlng = new google.maps.LatLng(pointHash['lat'], pointHash['lon']);
                 var img = new google.maps.MarkerImage('http://chart.apis.google.com/chart?cht=mm&chs=12x16&chco=FFFFFF,'+pointHash['color']+',000000&ext=.png');
		 
                 var marker = new google.maps.Marker({
                    icon: img,
                    position: latlng,
		    map: map,
		    title: null	    //needed, or adding a title later doesn't work...
                 });

		 if (!(typeof pointHash['title'] === 'undefined')) {
		    marker['title'] = pointHash['title']; }
 
                 if (!(app in destructableStuff)){
                    destructableStuff[app] = {}
                 }
                 if (!(type in destructableStuff[app])){
                   destructableStuff[app][type] = []
                 }
                 destructableStuff[app][type].push(marker);
              });
            };
        });
      });
    }
    
    else{
      $.each( destructableStuff[app][type], function(index, shape){
        shape.setMap(null);
      })
    }
  }

  function handleAppToggle(app){
    if($("input[data-type='" + app +"']").is(':checked')){
        
        $.each(jsonData[app], function(type, metaHash){
	  var color = metaHash['color']
	  alert(metaHash['title']);
	  if (typeof metaHash['title'] === 'undefined') {
	    title = type;  }
	  else { title = metaHash['title']; };

          $("#"+app+"_app_list").append("<li>\
            <span class='color-box' style='background: "+color+";'></span>\
            <input type='checkbox' data-type='"+type+"' class='map-option-"+app+"'>"+title+"\
          </li>");
        });

        $( ".map-option-"+app ).click(function() {
          handleOptionToggle( $(this).attr("data-type"), app )
        });

        destructableStuff[app] = {}
    }
    
    else{
      $("#"+app+"_app_list").html("");
      $.each( destructableStuff[app], function(index, option){
        $.each( destructableStuff[app][index], function(index, shape){
          shape.setMap(null);
        })
      })
    }
  }
  //Try this one first 

  $.getJSON("apps/", function( data ) {
    //alert("load");
    })

    .always( function() {
      $.each(jsonData, function(appName, appOptions){

          $("#map_interface_apps").append("<li>\
            <input type='checkbox' data-type='"+appName+"' class='app-option'>"+appName+"\
            <ul id='"+appName+"_app_list' class='options'></ul>\
          </li");
        });
    $( ".app-option" ).click(function() {
      handleAppToggle($(this).attr("data-type"))
    });

    //If there is only one app, it doesn't make sense to start with everything unchecked.
    if (Object.keys(jsonData).length == 1){
      var appName = Object.keys(jsonData)[0]
      $("input[data-type="+appName+"]").prop("checked",true);
      handleAppToggle(appName);
    };
  });
}
