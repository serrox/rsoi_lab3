import flask, json, math
from hashlib import md5
from db import db

def run():
	app = flask.Flask(__name__)

	@app.route('/users/<id>', methods=['GET'])
	def users_get_by_id(id):
		q = "SELECT email, name, description, cv FROM users WHERE id = '" + id + "'"
		query_result = db.exec_query(q).fetchone()

		if not query_result:
			flask.abort(404)

		
		
		user = {
			'id': id,
			'email': query_result[0],
			'name': query_result[1],
			'description': query_result[2],
		}

		return json.dumps({'user': user}), 200

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
