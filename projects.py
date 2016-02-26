import flask, json
from db import db

def run():
	app = flask.Flask(__name__)

	@app.route('/project/<id>', methods=['GET'])
	def get_project(id):
		q = "SELECT name, image, type, CVs FROM projects WHERE project_id = '" + id + "'"
		r = db.exec_query(q).fetchone()

		if not r:
			flask.abort(404)

		return json.dumps({'name': r[0],
			'image' : r[1],
			'type'  : r[2],
			'CVs'   : json.loads(r[3])
			}), 200

	app.run(port=8003, debug=True)

run()
