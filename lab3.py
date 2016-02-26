import flask, json
import requests

SESSION_BACKEND_LOCATION  = 'http://127.0.0.1:8001/'
USERS_BACKEND_LOCATION    = 'http://127.0.0.1:8002/'
PROJECTS_BACKEND_LOCATION = 'http://127.0.0.1:8003/'
MEDIA_BACKEND_LOCATION    = 'http://127.0.0.1:8004/'


def _request_get(host, url, request):
	print("SEND GET REQUEST TO {}{}".format(host, url))
	try:
		response = requests.get(host + url, params=request)
		result = response.json()
	except ValueError:
		return {"reason": "Can't understand the answer"}, 500
	except requests.exceptions.ConnectionError as e:
		print(e)
		return {"reason": "Service Unavailable"}, 503

	return result, response.status_code


def _request_post(host, url, request):
	print("SEND POST REQUEST TO {}{}".format(host, url))
	try:
		response = requests.post(host + url, data=request)
		result = response.json()
	except ValueError:
		return {"reason": "Can't understand the answer"}, 500
	except requests.exceptions.ConnectionError as e:
		print(e)
		return {"reason": "Service unavailable"}, 503

	return result, response.status_code


def _request_delete(host, url, request):
	print("SEND DELETE REQUEST TO {}{}".format(host, url))
	try:
		response = requests.delete(host + url, data=request)
		result = response.json()
	except ValueError:
		return {"reason": "Can't understand the answer"}, 500
	except requests.exceptions.ConnectionError as e:
		print(e)
		return {"reason": "Service unavailable"}, 503

	return result, response.status_code


def check_session():
	try:
		session = flask.request.cookies.get('session')
	except ValueError:
		return None
	if session is None:
		return None
	response, code = _request_get(SESSION_BACKEND_LOCATION,'session/{}'.format(session), None)
	if code == 200:
		return response['user_id']
	if code == 503:
		raise RuntimeError

	return None

def run_server():
	app = flask.Flask(__name__)

	@app.route("/", methods=["GET"])
	def main_page():
		server_error=False
		session = False
		try:
			if check_session():
				session = True
		except RuntimeError:
			server_error = True
		return flask.render_template('index.html', session=session, server_error=server_error)
	
	@app.route("/", methods=["POST"])
	def main_page_p():
		print(flask.request.form)
		try:
			l = flask.request.form["LogOutButton"]
		except:
			flask.abort(400)
		redirect = flask.redirect('/')
		page_response = flask.current_app.make_response(redirect)
		page_response.set_cookie('session', value='')
		return redirect
	
	@app.route("/register", methods=["GET"])
	def reg_page_get():
		return flask.render_template("registration.html")
	
	@app.route("/register", methods=["POST"])
	def reg_page_post():
		return

	@app.route("/login", methods=["GET"])
	def get_login():
		redirect = flask.redirect('/')

		try:
			if check_session():
				return redirect
		except RuntimeError:
			return 'Session service temporary unavailable'

		return flask.render_template("login.html")

	@app.route("/login", methods=["POST"])
	def post_login():
		try:
			email = flask.request.form["email"]
			password = flask.request.form["pass"]
		except:
			flask.abort(400)

		try:
			if check_session():
				return redirect
		except RuntimeError:
			return 'Session service temporary unavailable'

		redirect = flask.redirect('/')
		
		response, code = _request_post(SESSION_BACKEND_LOCATION, 
			'session',
			{
				'email': email,
				'password': password,
			}
		)

		if code == 403:
			return 'Wrong login or password'

		if code != 201:
			flask.abort(503, "Session Service Unavailable")

		page_response = flask.current_app.make_response(redirect)
		page_response.set_cookie('session', value=response['session'])
		return redirect

	@app.route("/me", methods=["GET"])
	def get_me():
		user_id = None
		try:
			user_id = check_session()
		except RuntimeError:
			return 'Session service temporary unavailable'
		if user_id is None:
			return flask.redirect('/login?url=/me')

		response, code = _request_get(USERS_BACKEND_LOCATION, 'users/{}'.format(user_id), None)
		print(response)

		if code == 200:
			proj = []
			for p in response['CV']['projects']:
				r, code = _request_get(PROJECTS_BACKEND_LOCATION, 'project/{}'.format(p), None)
				if code == 200:
					proj.append({'id' : p, 'name' : r['name']})
			return flask.render_template("me.html", name = response['user']['name'], email=response['user']['email'] ,description=response['user']['description'],
				cv_name = response['CV']['name'], Profession = response['CV']['profession'], projects = proj)

		flask.abort(503)

	@app.route("/cv", methods=["GET"])
	def get_cv():
		return

	@app.route("/photo", methods=["GET"])
	def get_photo():
		return

	@app.route("/video", methods=["GET"])
	def get_video():
		return

	@app.route("/record", methods=["GET"])
	def get_record():
		return

	@app.route("/project", methods=["GET"])
	def get_project():
		return

	@app.route("/search", methods=["GET"])
	def get_serach():
		return

	app.run(debug=True, port=8086)
	
run_server()