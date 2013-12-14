'''
Where We Meet

Tools for constructing a google map with contour lines of areas easiest for members of a group to get to.
 
Written by Elliot Hallmark (permafacture@gmail.com)

Free to use.  Have fun.
'''
#This Module needs to be able to open data files relative to __init__.py
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'

from numpy import arange, linspace, zeros #is aranged still used?
import csv
import brewer2mpl
almostblack = '#262626'

#lat, long of boundry defining points
ur = [30.494243, -97.430981] #lat,long of lower left corner of area to consider
ll = [30.116622, -97.76881] #lat,long of upper right corner of area to consider

center = [(ll[0]+ur[0])/2,(ll[1]+ur[1])/2]

gridfilename = BASE_DIR+'data/_gridfile.csv'
    
def get_contour_paths(filename, n=10):
    '''Uses gridfile and the file at 'filename' to return contour paths, colors and values''' 
    #TODO: currently this plot is rotated with respect to google map
    import matplotlib.pyplot as plt
    global BASE_DIR, gridfilename
    filename = BASE_DIR+filename
    Xs = []
    Ys = []
    Zs = []
    #extract data from files
    with open(gridfilename, 'rb') as grid:
        #not using with..as because filename could be file or array
        data = open(filename,'rb') 
        grid_reader = csv.reader(grid, delimiter='\t', quotechar='"')
        data_reader = csv.reader(data, delimiter='\t', quotechar='"')
        for datarow in data_reader:
            gridrow=grid_reader.next()
            gridrow=gridrow.__iter__()
            row = []
            for item in datarow:
                gitem = gridrow.next()
                gitem = tuple(eval(gitem, {'__builtins__':None}, {}))
                Xs.append(gitem[0])
                Ys.append(gitem[1])
                row.append(item)
            Zs.append(row)
    #plt.figure()
    #filter Xs and Ys to be what contour expects. the Xs and Ys of a grid
    m = len(Zs[0])
    Xs = Xs[:m]
    Ys = Ys[::m]
    C = plt.contour(Xs,Ys,Zs,n)
    #plt.show()
    levels = []
    colors = []
    for collection in C.collections:
	print "type: {}".format(type(collection))
        #colors.append(collection.get_color())
        ps = []
        for p in collection.get_paths():
          #if p.codes:
	  #  print ':: {}\n'.format(p.codes)
          ps.append(list(map(list,p.vertices)))
        levels.append(ps)
    #paths, colors of paths, and values represented by paths
    return levels,colors,C.levels

def sum_files(source_path="data/",save_file='_sumfile.csv'):
    '''create a file that sums all the travel times from all csv that 
    don't start with '_' in path.'''
    import os
    path=source_path
    #first determine size of the grid from _gridfile.csv
    with open(gridfilename,'rb') as f:
     r = csv.reader(f,delimiter='\t', quotechar='"')
     c=0
     for row in r:
        c+=1
    result = zeros((c,len(row)))

    #now iterate through files and sum fields
    for f in os.listdir(path):
        ff = os.path.join(path,f)
        if f[0] != '_' and f[-3:] == 'csv' and os.path.isfile(ff):
          #print "ff",f
          with open(ff,'rb') as fff:
            r = csv.reader(fff,delimiter='\t', quotechar='"')
            print 'open'
            for i,row in enumerate(r):
                for j,item in enumerate(row):
                    result[i][j] += float(item)

    #turn result into a file.  I thought I could use the array directly but guess not
    with open(os.path.join(path,save_file),'wb') as f:
        w = csv.writer(f,delimiter='\t', quotechar='"')
        for row in result:
            w.writerow(row)
    
    return result

_levels = ["Start"]
_colors = ['#555555']

n = 5
_levels = range(n)
colors = brewer2mpl.get_map('YlOrBr', 'Sequential', n)
hexcolors = colors.hex_colors

_colors = hexcolors

def options():
    global _levels,_colors
    ret_dict = {}
    for i in range(len(_levels)):
	ret_dict[_levels[i]] = _colors[i]
    print "Where we meet options: \n%s" % ret_dict
    return ret_dict

def data(query):
    '''Return the JSON hash result of this app'''
    global _levels,_colors
    i = int(query)
    #note, n is limited by max number colors in brewer map
    n=5
    levels,matplotlib_colors,legend = get_contour_paths('data/_sumfile.csv',20)
    
    colors = brewer2mpl.get_map('YlOrBr', 'Sequential', n)
    hexcolors = colors.hex_colors
    m = len(hexcolors)
    #_levels = legend
    #_colors = hexcolors
    #TODO: Make json_hash['poygon']=list() to keep ordering, duh
    json_hash = {'polygon':dict()}
    old = []
    print "legend: {}".format(legend[i])
    working_dict = {'strokeColor':almostblack,
	    'fillColor':hexcolors[i],
	    'fillOpacity':0.4,
	    'meta':list(),
	    'paths':list()}
    ### WARNING: key should be legend[i], not i, but this is a temp fix
    json_hash['polygon'][i]=working_dict
    working_dict['meta'].append([
	    'This is where the meta for level {} would be.'.format(i)])
    tmp = list() #all polygons of this level are in the same set
    for n,path in enumerate(levels[i]):
            p =  map(list,path)
	    tmp.append(p)
    if i != 0:
	#cut out the hole for the layer before it also
	for n,path in enumerate(levels[i-1]):
            p =  map(list,path)
	    p.reverse()
	    tmp.append(p)

    working_dict['paths'].append(tmp)

    return json_hash
