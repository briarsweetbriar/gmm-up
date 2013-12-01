import os
import shapefile as shp
import pyproj as proj
'''
Note: doing the map projection is stupid difficult to get information on.
You can use the .prj file to determine the epsg code, which pyproj recognizes
http://prj2epsg.org/search

Shape file specification: http://www.esri.com/library/whitepapers/pdfs/shapefile.pdf
'''

def make_lines(parts,points):
    '''take ESRI line parts and points and make plotable sections of lines'''
    result = []
    if len(parts)>1:
	begin = parts[0]
	for end in parts[1:]:
	    #print begin, end, points[begin:end]
	    result.append(points[begin:end])
	    begin = end
    else:
	result = [points]
    return result

def make_polygons(parts,points):
    '''take ESRI line parts and points and make plotable sections of lines'''
    result = []
    if len(parts)>1:
	begin = parts[0]
	for end in parts[1:]:
	    #print begin, end, points[begin:end]
	    result.append([list(point) for point in points[begin:end]])
	    begin = end
    else:
	result.append(points)
    #make result an extra list deep so that we can iterate line points and polygons in the
    #same way but polygons are passed to googlemaps as an array of arrays, to the holes 
    return [result]



BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'

class GISRecords(object):
    '''GISRecord object takes a .shp file, knows its own epsg code and can transform (project) its own points.'''

    #when testing bounding box overlap, and returning points, 
    #make sure not to use more points than this (evenly distributed)
    max_length = 30 
    feet = True	#is .shp file defined in feet? or meters?

    def __init__(self, shpfile, epsgcode, base_dir=BASE_DIR):
	self.epsgcode = epsgcode
	print "loading records..."
	reader = shp.Reader(os.path.join(BASE_DIR,shpfile))
	self.records = reader.shapeRecords()
	print "{} loaded".format(shpfile)
	print '\nmetadata of first record (for example):'
	print self.records[0].record

    def make_shapes(self,record):
	'''determine ESRI shape type from record and process points into shape dictionary:
	    {'points':record.shape.points,'lines':[line1,line2],'polygons':[poly1,poly2]}
        '''
	points = record.shape.points
        points = self.transform_points(points)
	shapetype = record.shape.shapeType
	#print shapetype
	result = {'points':points,'lines':[],'polys':[]}
    
        if shapetype == 3:
	    #line
	    parts = record.shape.parts
	    result['lines'] = make_lines(parts,points)
	if shapetype == 5:
	    #polygon
	    parts = record.shape.parts
	    result['polys'] = make_polygons(parts,points)

        #print 'result: ',result,'\n\n\n\n'     
	return result


    def records_of_type(self,field,to_match=''):
	'''
	Take an integer field # and a string to search for.
	Return the points and metadata for all records where 
	field value matches the search string. 

        to_match can be a string or list of strings like 'sf-2'

	return value is a list of dictionaries of dictionaries of lists

	return [ {matchtype1:
		{'shapes':[[points1],[points2]],'meta':[[meta1],[meta2]]}},
		
		{matchtype2:
		{'shapes':[[points1],[points2]],'meta':[[meta1],[meta2]]}},
		
		...]

	Points are transformed and ready to map.

	'''
        tmp = {}
        if type(to_match) == str:
            to_match = set([to_match])
        elif type(to_match) == list:
	    to_match = set(to_match)
        for record in self.records:
            fieldvalue = record.record[field]
            if (not to_match) or (fieldvalue in to_match):
                #add record, creating key if necessary            
                tmp.setdefault(fieldvalue, []).append(record)
	result = {}
	#print tmp
	for key,value in tmp.items():
	    #key is field name, value is record.  Explode record
	    result[key] = {'shapes':[],'meta':[]}
	    for record in value:
	      #if len(record.shape.parts) > 1:   #only complex polygons please
		result[key]['shapes'].append(self.make_shapes(record))
		result[key]['meta'].append(record.record)

        return result

  
    def overlaps_boundingbox(self, pts, c1, c2):
        '''return True is one point in record is in the bounding box 
	defined by corner1 and corner2.
        '''
        return True in [self.in_rec(pt, c1, c2) for pt in pts]

     
    def record_field_possibilities(self, field=0, corner1 = None, corner2=None):
        '''
        Return a dictionary keyed by the *set* of all data defined in he given field
        with values equal to the count of fields that have that exact name.
    
        GIS metadata from records might look like ['address', 'zone','crime idx']
        so field 1 refers to all the zones.  Return dictionary might look like
        {'residential':243}. I found field names defined in .dbf files that
        came with the .shp and .prj files.
        
        May be geoprahically filtered by defining corner1 and corner2.
        There may be WAY to many points in the shape to test all of them 
        for being inside the bounding box, so bb_accuracy defines the max number of
        points to test (evenly distributed along total point list), or None to use
        all points'''
        s = {}
        for record in self.records:
            if corner1 and corner2:
		pts = self.transform_points(record.shape.points)
                if self.overlaps_boundingbox(pts,corner1,corner2):
                    trash = s.setdefault(record.record[field],0)
                    s[record.record[field]] +=1
            else:
                trash = s.setdefault(record.record[field],0)
                s[record.record[field]] +=1
        return s
       
    def transform_points(self,points):
	'''.shp points are defined weird, and need to be projected
	using the epsgcode'''
        converter = proj.Proj(init=self.epsgcode)
        conv = 1 
        if self.feet:
            conv = .3048
        result = []
        for pt in points:
            lon,lat = converter(pt[0]*conv,pt[1]*conv,inverse=True)
            result.append((lat,lon))
        return result
    
    def bbox_to_points(bbox):
        #bbox from pyshp shape bbox is list of two corners
        c1x,c1y,c2x,c2y = bbox
        return [(c1x, c1y), (c1x,c2y), (c2x,c2y), (c2x, c1y), (c1x, c1y)]
    
    def in_rec(p, c1, c2):
        #is p in the rectangle defined by corners c1 and c2?
        #return True if so.
        xmax, xmin = max(c1[0],c2[0]), min(c1[0],c2[0])
        ymax, ymin = max(c1[1],c2[1]), min(c1[1],c2[1])
        return xmin < p[0] < xmax and ymin < p[1] < ymax
    

    
if __name__ == '__main__':
    from googlemaps import GoogleMaps,GoogleMapsError
    import pprint
    import pygmaps

    zoning_epsgcode= 'epsg:3663' #for central texas zoning map
    zoning_shpfile = 'zoning/zoning.shp'
    zoningrecords = GISRecords(zoning_shpfile,zoning_epsgcode)
    zoningrecords.max_length = 50
    zoning_field = 5	#got this from .dbf file next to .shp file

    #unecessarily generous corners:
    pt1 = [30., -98.]
    pt2 = [30.4, -97.]

    #corners of area considered
    c1,c2 = pt1, pt2
    mymap = pygmaps.maps(pt1[0], pt1[1], 10)
    #fancy flatten list.  Overkill for such a short list but repitition leads to rememberance
    #mymap.addpath(bbox_to_points([item for sublist in [c1,c2] for item in sublist]),fillcolor='#444444',opacity=.2)


    #get all the zones that are derivatives of these basic types
    base_types = ['GO', 'LR', 'GR', 'CBD', 'DMU', 'CS', 'CS', 'CH']
    all_types = zoningrecords.record_field_possibilities(field=zoning_field)
    valid_types = []
    print "the following zones were found: "
    for key,value in all_types.items():
        if key[:2] in base_types:
            print key, value
            valid_types.append(key)
    zonedict = zoningrecords.records_of_type(zoning_field,valid_types)
    #housing = {'everything':records}
    for zone,datadict in zonedict.items():
        print "mapping zone type: ", zone 
        for shapedict in datadict['shapes']:
	    for line in shapedict['lines']:	
		mymap.addpath(line,color='#0000FF',opacity=0)	
	    for poly in shapedict['polys']:
		mymap.addpath(poly,color='#0000FF',fillcolor='#0000FF',opacity=.5)


    mymap.draw('./gis_TEST.html')

