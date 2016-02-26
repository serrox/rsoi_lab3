import flask, json,datetime
from hashlib import md5, sha512
from db import db


def run():
	app = flask.Flask(__name__)

	@app.route("/session/<id>", methods=['GET'])
	def session_get(id):
		def check_session(session):
			q = "SELECT * FROM sessions WHERE session_id = '" + session + "'"
			r = db.exec_query(q).fetchone()

			if r:
				current_time = datetime.datetime.now()
				expires = datetime.datetime.strptime(r[2].split('.')[0], '%Y-%m-%dT%H:%M:%S')
				if  current_time < expires:
					return r[1]
			return False

		try:
			user_id = check_session(id)
		except TypeError:
			return json.dumps({'reason': 'Service Unavailable'}), 503

		if user_id:
			return json.dumps({'user_id': user_id}), 200
		else:
			return json.dumps({'reason': 'Not found'}), 404
	
	@app.route('/session', methods=['POST'])
	def session_post():
		def create_login_hash(email, password):
			return md5((email+"salt"+password).encode("utf-8")).hexdigest()

		def get_user(email, hash):
			q = "SELECT id FROM users WHERE hash = '" + hash + "' AND email = '" + email + "'"
			users = db.exec_query(q).fetchall()
			if len(users) > 0:
				return users[0][0]
			else:
				return None

		def create_session(hash):
			current_time = datetime.datetime.now()
			expire_time = current_time + datetime.timedelta(days=30)

			session = sha512((hash+str(current_time)+'s').encode('utf-8')).hexdigest()

			q = "INSERT INTO sessions VALUES ('" + session +"', '" + user_id + "', '" + expire_time.isoformat() + "')"
			print(q)
			db.exec_query(q)
			db.commit()

			return session

		try:
			email =  flask.request.form['email']
			password =  flask.request.form['password']
		except:
			flask.abort(400)

		hash = create_login_hash(email, password)
		user_id = get_user(email, hash)
		if user_id:
			try:
				session = create_session(hash)
			except TypeError:
				return json.dumps({'reason': 'Service Unavailable'}), 503
			return json.dumps({'session': session}), 201
		else:
			return json.dumps({'reason': 'Wrong login or password'}), 403

	app.run(port=8001, debug=True)

run()