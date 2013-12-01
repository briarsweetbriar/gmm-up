#!/usr/bin/python
import gis
import json
import brewer2mpl
almostblack = '#262626'

zoning_epsgcode= 'epsg:3663' #for central texas zoning map
zoning_shpfile = 'zoning/zoning.shp'
zoningrecords = gis.GISRecords(zoning_shpfile,zoning_epsgcode)
zoningrecords.max_length = None #don't make this None!
zoning_field = 5	#got this from .dbf file next to .shp file

def condense_dict(dictionary,explode_param = '-'):
    '''
    condense a dictionary so that the values of similar keys are all kept under a common key
    input:
	dictionary: the dictionary to condense
	explode_param: truncate keyes up to this. if integer, then shorten keys to that length.
			if a string, then shorten keys to be up to that value

    returns condensed dictionary
    '''
    retdict = {}
    for key,value in dictionary.items():
	#This is very performance uncritical, or else I'd use a fancy technique to take this if/else out of the loop
	if type(explode_param) == int:
	    condensed_key = key[:explode_param].strip()
	elif type(explode_param) == str:
	    condensed_key = key.split(explode_param)[0].strip()
	else:
	    print "explode_param should be an int or string, got {} instead".format(type(explode_param))
	    raise TypeError

	retdict.setdefault(condensed_key,list()).append(value)
    return retdict


def zone_me(qtype):
    '''Takes qtype = name of zone to return, ie "GO"
    returns a dictionary like:
    {'polygon':
      {zoneType:
        {'strokeColor':'#262626',
         'fillColor':'#A6CEE3',
         'fillOpacity':0.5,
         'paths':
           [ [ [p1,p2,p3],], [poly2,holeinpoly2], ]
         }
       }
     }
    '''


    '''
    #get all the zones that are derivatives of these basic types
    base_types = ['GO', 'LR', 'GR', 'CBD', 'DMU', 'CS', 'CS', 'CH']
    #base_types = ['GO']
    all_types = zoningrecords.record_field_possibilities(field=zoning_field)
    valid_types = []
    #print "the following zones were found: "
    for key,value in all_types.items():
        if key[:2] in base_types:
            #print key, value
            valid_types.append(key)
    '''
    valid_types = [qtype]
    zonedict = zoningrecords.records_of_type(zoning_field,valid_types)

    ## Make things pretty with colors
    zonedict = condense_dict(zonedict,explode_param='-')
    number_of_zones = len(zonedict)
    print "condensed zone set has {} zone types".format(number_of_zones)
    if number_of_zones < 3: number_of_zones = 3
    colors = brewer2mpl.get_map('Paired', 'Qualitative', number_of_zones)
    hexcolors = colors.hex_colors
    n = 0   #for colors

    json_hash = {'polygon':{}}
    for zone,condensed_data in zonedict.items():
      #zone='L57'
      #I know there's only polygons, so no need to use a more robust method
      json_hash['polygon'][zone]={}
      cntr = 0
      for datadict in condensed_data:	
        json_hash['polygon'][zone]['fillColor'] = hexcolors[n]
	json_hash['polygon'][zone]['fillOpacity'] = 0.5
	json_hash['polygon'][zone]['strokeColor'] = almostblack
	json_hash['polygon'][zone]['paths'] = []
        for shapedict in datadict['shapes']:
	    for listofpoints in shapedict['polys']:
		#print "_ %s _"%listofpoints
		json_hash['polygon'][zone]['paths'].append(listofpoints)    
		cntr+=1
      print "mapping {cntr} of zone type {zone} in {color}".format(zone = zone, cntr=cntr,color=hexcolors[n])
      n+=1
    
    return json_hash   
