#!/usr/bin/python
from csv import DictReader
from os import path, listdir

data_dir = './example_data'

def csv_2_markers(infile):
    '''takes a filename and returns a list of dictionaries with keys 'lat', 'lon', 'color','title' '''
    with open(infile, 'rb') as f:
      reader = DictReader(f, delimiter='\t')
      result = []
      color = '000000'
      for i,row in enumerate(reader):
        tmp = dict()

	try:
	    tmp['lon'] = row['lon']
	    tmp['lat'] = row['lat']
	except KeyError:
	    print '%s was malformed. needs "lat" and "lon" columns.' % filename
	    break

	try:
	    tmp['color'] = str((row['color']).replace('#',''))
	    color = tmp['color']
	except AttributeError:
	    #if only one point has a color, those after it will have the same color
	    tmp['color'] = color
	except KeyError:
	    #if only one point has a color, those after it will have the same color
	    tmp['color'] = color

	try:
	    tmp['title'] = row['title']
	except KeyError:
	    pass

        tmp['text'] = 'This marker #%s. Have a <em>nice day</em>' % i
	result.append(tmp)
    return result, '#%s' % color

def csv_2_lines(infile):
    '''takes a filename and returns a list of dictionaries with keys 'path':[[lat, lng],], 
	'color', and optionally, 'editable' '''
    with open(infile, 'rb') as f:
      reader = DictReader(f, delimiter='\t')
      result = []
      color = '#000000'
      pathtmp = {'path':list()}
      for row in reader:

	try:
	    lng = row['lon']
	    lat = row['lat']
	    if not lng or not lat:
		raise KeyError
	except KeyError:
	    #blank or malformed line.  Time to start a new path
	    #if you start with a blank line, you DESERVE a bug
	    #BUG: an empty row is IGNORED by DictReader.
	    #	 row must have something in it to trigger this error!
	    result.append(pathtmp)
	    pathtmp = {'path':list()}
	else:
	    pathtmp['path'].append([lat,lng])

            try:
                if not row['color']:
            	  #print "Called"
            	  raise KeyError
                else:
            	  color = '#'+row['color']
            	  pathtmp['color'] = color
            except AttributeError:
                #if only one point has a color, those after it will have the same color
                pathtmp['color'] = color
            except KeyError:
                #if only one point has a color, those after it will have the same color
                pathtmp['color'] = color
                #print color
            
            try:
                pathtmp['editable'] = str(row['editable'] in ['true','True']).lower() 	#turn None to false
            except KeyError:
                pathtmp['editable'] = 'false'
	
    #one more push to put whatever is left into the result
    result.append(pathtmp)
    return result, color


def build_data():
    '''
	See definition of data expected in main.js
    '''
 
    result = []
    x = path.join	    #shorthand later
    #first directory level is app names
    appnames = [y for y in listdir(data_dir) if path.isdir(x(data_dir,y))]
    appnames.sort()
    for app in appnames:
        tmp = {'id':app, 'title':app.replace('_',' ').capitalize()}
        #second level is data-group name
	datanames = [y for y in listdir(x(data_dir,app)) if path.isdir(x(data_dir, x(app, y)))]
        datanames.sort()
	for dataset in datanames:
	    tmp[dataset] = dict()
	    tmp[dataset]['title'] = " ".join([xxx.capitalize() for xxx in dataset.split("_")])
	    #last level is primitive name
	    primnames = [y[:-4] for y in listdir(x(data_dir,x(app,dataset))) if y[-4:] == '.csv']
	    for primitive in primnames:
		#note: calling function by name
		tmp[dataset][primitive], tmp[dataset]['color'] = globals()['csv_2_%s' % primitive](x(data_dir,x(app, x(dataset, x('%s.csv' % primitive)))))
        result.append(tmp)
    return result

def build_page(data):
    '''
    Compile stylesheets, javascript, html, and generated data into one html file
    data is a dictionary. See definition in main.js'''

    import bs4
    from jsmin import jsmin
    soup = bs4.BeautifulSoup(open("index.html").read())

    stylesheets = soup.findAll("link", {"rel": "stylesheet"})
    for s in stylesheets:
	t = soup.new_tag('style')
	c = bs4.element.NavigableString(open(s["href"]).read())
	t.insert(0,c)
	t['type'] = 'text/css'
	s.replaceWith(t)

    #insert data into javascript file
    jsonMarker ='/* INSERT JSON DATA HERE */' 
    jsonData = str(data)[1:-1]	#strip the outer {} because it is being inserted into {}
    #print jsonData
 
    javascripts = soup.findAll("script")
    for s in javascripts:
	t = soup.new_tag('script')
	#print s['src']
	if s['src'][:4] != 'http':
	    c = bs4.element.NavigableString(jsmin(open(s["src"]).read().replace(jsonMarker,jsonData)))
	    t.insert(0,c)
	    t['type'] = 'text/javascript'
	    s.replaceWith(t)


    open("output.html", "w").write(str(soup.prettify(formatter=None)))


center = [30.320000, -97.770000]

'''http://stackoverflow.com/questions/7494474/google-maps-api-polygon-with-hole-in-center'''
polygon = [[[[25.774252, -82.190262],[17.466465, -65.118292],[34.321384, -63.75737],[25.774252, -82.190262]],[[25.774252, -80.190262],[32.321384, -64.75737],[18.466465, -66.118292],[25.774252, -80.190262]]]]

center = [(polygon[0][0][0][0] + polygon[0][0][1][0]+polygon[0][0][2][0])/3.,(polygon[0][0][0][1] + polygon[0][0][1][1]+polygon[0][0][2][1])/3.]

dd = {'id' : 'app2',       #used for tag names
      'title': 'Example #2',   #used for display
      'dataset1': { 
        'color': '#0000FF', #color to display on key
	'title': 'Polygon Example',
	'polygons' : [{'polygon':polygon, 
	     'fillColor': '#0000FF',
	     'fillOpacity': 1,
	     'strokeColor':'#000000'  
	          }],
        'markers' : [{'lat':center[0],'lon':center[1],'color':'#FF0000','title':'Click Me!','text':'The <strong>center</strong> of the <a href="http://en.wikipedia.org/wiki/Bermuda_Triangle">Bermuda Triangle</a>!'}]
         }
     }

if __name__ == '__main__':
  ff = build_data()
  ff.append(dd)
  build_page(ff)
