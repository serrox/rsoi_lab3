import flask, json, math
from hashlib import md5
from db import db

def run():
	app = flask.Flask(__name__)

	@app.route('/users/<id>', methods=['GET'])
	def get_user(id):
		q = "SELECT email, name, description, cv_id FROM users WHERE id = '" + id + "'"
		query_result = db.exec_query(q).fetchone()

		if not query_result:
			flask.abort(404)

		q = "SELECT name, profession, projects_id, videos_id, records_id, photos_id FROM CVs WHERE cv_id = '" + str(query_result[3]) + "'"
		r = db.exec_query(q).fetchone()
		
		user = {
			'id': id,
			'email': query_result[0],
			'name': query_result[1],
			'description': query_result[2]
		}

		if not r:
			CV = {}
		else:
			CV = {
				'name' : r[0],
				'profession' : r[1],
				'projects' : json.loads(r[2]),
				'videos' : json.loads(r[3]),
				'records' : json.loads(r[4]),
				'photos' : json.loads(r[5])
			}

		return json.dumps({'user': user, "CV" : CV}), 200

	@app.route('/cv/<id>', methods=['GET'])
	def get_cv(id):
		q = "SELECT name, profession, projects_id, videos_id, records_id, photos_id, image FROM CVs WHERE cv_id = '" + id + "'"
		r = db.exec_query(q).fetchone()

		if not r:
			flask.abort(404)

		return json.dumps({
			'name' : r[0],
			'profession' : r[1],
			'projects' : json.loads(r[2]),
			'videos' : json.loads(r[3]),
			'records' : json.loads(r[4]),
			'photos' : json.loads(r[5]),
			'image' : r[6]
		}), 200

	@app.route('/users', methods=['POST'])
	def users_post():
		try:
			email = flask.request.form['email']
			password = flask.request.form['password']
			name = flask.request.form['name']
		except:
			return flask.abort(400)

		hash = md5((email+'salt'+password).encode('utf-8')).hexdigest()
		id = md5((email+'salt').encode("utf-8")).hexdigest()

		q = "SELECT id FROM users WHER id = '" + id + "'"
		r = db.exec_query(q).fetchone()

		if len(r) > 0:
			return json.dumps({'reason': 'Wrong login or password'}), 403

		q = "INSERT INTO users VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
			id,
			hash,
			email,
			name,
			'',
			''
		)

		db.exec_query(q)
		db.commit()

		return json.dumps({'reason':'Registration complete'}), 201


	app.run(port=8002, debug=True)

run()
