#!/usr/bin/python
'''
A Server to respond to ajax requests from the gmm-up javascript front end.

'''


from flask import Flask, jsonify,send_from_directory,request

import zoning
import WhereWeMeet

#Set up flask server
app = Flask(__name__,static_folder='static')

#name the apps this server can provide
apps = ["zoning","travel-time"]
myapp = None  #Initial app loaded.  None right now

def get_app(appstring):
    '''Set which app is going to be responding to requests'''
    if appstring == 'zoning':
	return zoning
    elif appstring == 'travel-time':
	return WhereWeMeet

#an example json response, incase you care to see.
json_response = {
  'polygon':
    {'L57':
      {'strokeColor':'#262626',
       'fillColor':'#A6CEE3',
       'fillOpacity':0.5,
       'paths':		 #paths = All of the sets of polygons
         [  #paths[0] = One set of polygons, whole and holes
          [    #paths[0][0] = one set of polygons
           [[30.265631, -97.720796],	#paths[0][0][0]= an individual polygon
	    [30.264739, -97.721215],	#paths[0][0][0][0] = 
	    [30.262647, -97.722196],
	    [30.263278, -97.724052],
	    [30.266618, -97.722513],
	    [30.265947, -97.720648],
	    [30.265631, -97.720796]],
	   [[30.263555, -97.722405],
	    [30.263457, -97.722083],
	    [30.263671, -97.721991],
	    [30.263769, -97.722323],
	    [30.263555, -97.722405]]
	  ]
         ]
       }
     }
 }

@app.route("/")
def hello():
    with open('index.html','rb') as f:
        return f.read()

@app.route("/apps/")
def give_apps():
    '''Just return the list of apps that are available'''		
    return jsonify({'apps':apps})

@app.route("/data/",methods=['GET', 'POST'])
def give_data():
    try:
	qtype = request.args['type']
	appstring = request.args['app']
    except KeyError:
	return None
    else:
	myapp = get_app(appstring)
	return jsonify(myapp.data(qtype))

@app.route("/app/",methods=['GET','POST'])
def give_options():
    try:
	appstring = request.args['app']
    except KeyError:
	return None
    else:
	myapp = get_app(appstring)
        return jsonify(myapp.options())

@app.route('/javascripts/<path:filename>')
def send_js(filename):
     with open('./javascripts/%s'%filename,'rb') as f:
        return f.read()

   

@app.route('/stylesheets/<path:filename>')
def send_css(filename):
     with open('./stylesheets/%s'%filename,'rb') as f:
        return f.read()


if __name__ == "__main__":
    import commands
    local_ip = commands.getoutput("/sbin/ip addr").split("\n")[10].strip().split(' ')[1].split('/')[0]

    app.run(local_ip,debug=True)
