
from flask import Flask, jsonify,send_from_directory,request

example = 1
if example == 0:
  import zoning as myapp
else:
  import WhereWeMeet as myapp

app = Flask(__name__,static_folder='static')

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

j_r = {'booger':'123'}

@app.route("/")
def hello():
    with open('index.html','rb') as f:
        return f.read()

@app.route("/data/",methods=['GET', 'POST'])
def give_data():
    try:
	qtype = request.args['type']
    except KeyError:
	return None
    else:
	return jsonify(myapp.data(qtype))

@app.route("/options/",methods=['GET','POST'])
def give_options():
     return jsonify(myapp.options())
'''    return jsonify({'This':'#453627'})
'''
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
