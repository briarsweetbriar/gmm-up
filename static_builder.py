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
      for row in reader:
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

	result.append(tmp)

    return result, '#%s' % color

def build_data():
    '''
	See definition of data expected in main.js
    '''
 
    result = {}
    x = path.join	    #shorthand later
    #first directory level is app names
    appnames = [y for y in listdir(data_dir) if path.isdir(x(data_dir,y))]
    for app in appnames:
	result[app] = dict()
        #second level is data-group name
	datanames = [y for y in listdir(x(data_dir,app)) if path.isdir(x(data_dir, x(app, y)))]
	for dataset in datanames:
	    result[app][dataset] = dict()
	    result[app][dataset]['title'] = " ".join([xxx.capitalize() for xxx in dataset.split("_")])
	    #last level is primitive name
	    primnames = [y[:-4] for y in listdir(x(data_dir,x(app,dataset))) if y[-4:] == '.csv']
	    for primitive in primnames:
		print primitive
		result[app][dataset][primitive], result[app][dataset]['color'] = csv_2_markers(x(data_dir,x(app, x(dataset, x('%s.csv' % primitive)))))
    #print result
    return result

def build_page(data):
    '''data is a dictionary. See definition in main.js'''

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
    print jsonData
 
    javascripts = soup.findAll("script")
    for s in javascripts:
	t = soup.new_tag('script')
	print s['src']
	if s['src'][:4] != 'http':
	    c = bs4.element.NavigableString(jsmin(open(s["src"]).read().replace(jsonMarker,jsonData)))
	    t.insert(0,c)
	    t['type'] = 'text/javascript'
	    s.replaceWith(t)


    open("output.html", "w").write(str(soup.prettify(formatter=None)))




if __name__ == '__main__':
  build_page(build_data())
