
/*

Accepts a hash table of data (defined within 
this file and/or provided by calls to the urls 
./apps and ./data), and renders the geometry 
to a google map. 

*/
function initialize() {

  var destructableStuff = {}

  /* jsonData is the master variable of all data within all of the apps

  has the following structure:
    data = [
            {'id' : 'app1'       //used for tag names
             'title': 'app #1'   //used for display
             'dataset1': { 
	       'color': '#00FF00' //color to display on key
	       'title': 'Data Set #1'
               'markers': [
                 { points to plot }, 
                 {'lat':37.220,'lon':-96.904,'color': '#000000', 'title':'pt1', 'text':'<strong>HTML here!</strong>}, //color of primitive
                 {'lat':30.384,'lon': -97.683,'title':'pt2'}, //same color as last one
                 {'lat':29.629,'lon': -98.492,'color':'#00FF00', 'title':'pt3'} // new color
                 ],
	       'lines : [
	         {path :[[lat,lng],list of coodrinates], 
	          color: '#0000FF', 
                  editable: True
	          },
	          { Second Line with path, color, editable keys}, 
                 ],
             },
            }      
           ]
    '''

  */
  var jsonData = [/* INSERT JSON DATA HERE */];  //Do not change this tag!

  var metaTags = ['title','id','options']; //apps may not have data sets with these names, they are reseved for app meta information

  $("input:checkbox").each(function( index ) {
    this.checked = false;
  });

  var centerlatlng = new google.maps.LatLng(30.320000, -97.770000);
  var myOptions = {
    zoom: 5,
    center: centerlatlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var infowindow = new google.maps.InfoWindow({
      content: 'Nothing to say, yet'
  });


  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

  function handleOptionToggle(type, app){
    if($("input[data-type='" + type +"']").is(':checked')){

      $.getJSON( "data/?&type=" + type + "&app=" + app, function( data ) {

        alert("todo: push this data into jsonData");
      })

      .always( function() {

        var appHash = {}; 
        $.each( jsonData, function( index, app_hash ) {
	    //go through and get app
            if (app_hash['id'] === app){
              appHash = app_hash; }
        });

        $.each (appHash[type], function(shape, shapeHash) {
          if (shape == "polygons") {
            $.each( shapeHash, function( index, polygonHash ){
	      $.each( polygonHash["polygon"], function( index, coordArray){
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
                  fillColor: polygonHash["fillColor"],
                  fillOpacity: polygonHash["fillOpacity"],
                  strokeColor: polygonHash["strokeColor"],
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
          }
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

		 //add a title now if it exists
		 if (!(typeof pointHash['title'] === 'undefined')) {
		    marker['title'] = pointHash['title']; }
		 
		 //add a listener to move / open an information window when the marker is clicked
		 if (!(typeof pointHash['text'] === 'undefined')) {
		   google.maps.event.addListener(marker, 'click', function() {
		      //TODO: add a div to this so it can be styled through the style sheet
		      infowindow.setContent(pointHash['text']);
		      infowindow.open(map,marker);
		      });
                   }
                 
 
                 if (!(app in destructableStuff)){
                    destructableStuff[app] = {}
                 }
                 if (!(type in destructableStuff[app])){
                   destructableStuff[app][type] = []
                 }
                 destructableStuff[app][type].push(marker);
              });
            };

           if (shape == "lines") {
              $.each( shapeHash, function(index,pathHash ){
		var path = [];
		$.each ( pathHash['path'], function(index,latlng) {
                  path.push( new google.maps.LatLng(latlng[0], latlng[1])); });	 
                var polyline = new google.maps.Polyline({
                    path: path,
                    strokeColor: pathHash['color'],
		    map: map,
		    geodesic: true,
		    strokeWeight: 2,
		    editable: false,	    //needed, or adding a later doesn't work...
                 });

		 if (!(typeof pathHash['editable'] === 'undefined')) {
                    //alert(pathHash['editable']);
		    polyline['editable'] = (pathHash['editable'] === 'true');
		     }
                 
                 if (!(app in destructableStuff)){
                    destructableStuff[app] = {}
                 }
                 if (!(type in destructableStuff[app])){
                   destructableStuff[app][type] = []
                 }
                 destructableStuff[app][type].push(polyline);
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
        
        var appHash = {}; 
        $.each( jsonData, function( index, app_hash ) {
	    //go through and get app
            if (app_hash['id'] === app){
              appHash = app_hash; }
        });


        $.each(appHash, function(type, metaHash){
          if ($.inArray(type,metaTags) === -1){
	    var color = metaHash['color']
	    if (typeof metaHash['title'] === 'undefined') {
	      title = type;  }
	    else { title = metaHash['title']; };

            $("#"+app+"_app_list").append("<li>\
              <span class='color-box' style='background: "+color+";'></span>\
              <input type='checkbox' data-type='"+type+"' class='map-option-"+app+"'>"+title+"\
            </li>");
         };
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
    }).
    
    always( function() {
      $.each(jsonData, function(index, appHash){
          var appId = appHash['id'];
          if (typeof(appHash['title']) === 'undefined') {
            var appTitle = appHash['id'];
          }
          else {
            var appTitle = appHash['title'];
          }
          $("#map_interface_apps").append("<li>\
            <input type='checkbox' data-type='"+appId+"' class='app-option'>"+appTitle+"\
            <ul id='"+appId+"_app_list' class='options'></ul>\
          </li");
        });
    $( ".app-option" ).click(function() {
      handleAppToggle($(this).attr("data-type"))
    });

    //If there is only one app, it doesn't make sense to start with everything unchecked.
    if (jsonData.length == 1){
      //alert('hello2');
      var appName = jsonData[0]['id']
      $("input[data-type="+appName+"]").prop("checked",true);
      handleAppToggle(appName);
    };
  });
}
/*
  //I stole this from the info window demo @ https://developers.google.com/maps/documentation/javascript/examples/infowindow-simple
  //Not sure what it does or if it is needed.
  google.maps.event.addDomListener(window, 'load', initialize);
*/
