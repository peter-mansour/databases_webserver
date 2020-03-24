import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, flash
from forms import *
from flask_bootstrap import Bootstrap
from queries import *
from tables import *

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'phm2122'
Bootstrap(app)

DATABASEURI = "postgresql://phm2122:9813@35.231.103.173/proj1part2"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

fnm = None
uid = None

@app.route('/', methods=['Get', 'POST'])
def index():
	form_login = Login()
	err_msg = None
	global fnm
	global uid
	if form_login.validate_on_submit():
		unm = request.form.get('username')
		pwd = request.form.get('password')
		if request.form.get('role'):
			cur = g.conn.execute(login_owner.format(unm=unm, pwd=pwd))
		else:
			cur = g.conn.execute(login_contrib.format(unm=unm, pwd=pwd))
		row = cur.first()
		if row:
			uid = row['user_id']
			fnm = row['first_name']
			flash('Successfully logged in!', 'error')
			return redirect(url_for('homepage'))
		else:
			err_msg = "Account does not exist"
	return render_template('index.html', form=form_login, err=err_msg)
	
@app.route('/signup', methods=['Get', 'POST'])
def signup():
	form_signup = SignUp()
	if form_signup.validate_on_submit():
		return render_template('signup_confirm.html')
	return render_template('signup.html', form=form_signup)
	
@app.route('/homepage', methods=['Get', 'POST'])
def homepage():
	new_proj = CreateProj()
	if new_proj.validate_on_submit():
		print("got form", flush=True)
	cur = g.conn.execute(get_projs.format(uid=uid))
	projs = []
	for row in cur:
		projs.append(Proj(row['description'], row['src_code_link'], row['imgage_path']))
	return render_template('homepage.html', new_proj=new_proj, fnm=fnm, projs=projs)
	
if __name__ == "__main__":
	app.run(debug=True)
	
"""
@app.route('/')
def index():
	print(request.args)
	cursor = g.conn.execute(query_1)
	names = []
	for result in cursor:
		names.append(result['name']) 
		cursor.close()
		context = dict(data = names)
	return render_template("index.html", **context)
	
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
  run()
"""