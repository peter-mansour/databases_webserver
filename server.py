import os
import sys
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, redirect, Response, url_for, flash
from forms import *
from flask_bootstrap import Bootstrap
from tables import *
import click
from utils import *

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = os.urandom(64)
Bootstrap(app)

rand.seed(1)
DATABASEURI = "postgresql://phm2122:9813@35.231.103.173/proj1part2"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
	try:
		g.conn = engine.connect()
	except:
		print("Failed to connect to database", flush=True)
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	try:
		g.conn.close()
	except Exception as e:
		pass

@app.route('/', methods=['Get', 'POST'])
def index():
	form_login = Login()
	err_msg = None
	if request.method == 'POST':
		if request.form['action'] == 'signin' and form_login.validate_on_submit():
			Session.client = UserUtils.signin(FormUtils.load_form_signin())
			if Session.client:
				flash('Successfully logged in!', 'error')
				return redirect(url_for('homepage'))
			else:
				err_msg = "Username or Password are Incorrect"
		elif request.form['action'] == 'signup':
			return redirect(url_for('signup'))
	return render_template('index.html', form=form_login, err=err_msg)

@app.route('/search', methods=['Get', 'POST'])
def search():
	search_bar = SearchBar()
	if request.method == 'POST':
		if search_bar.validate_on_submit():
			content = request.form.get('search_val')
			search_type = request.form.get('search_by')
			print(content, search_type, file=sys.stdout)
			if search_type == '0':#search project by name
				projs = ProjUtils.load_projs_by_name(content)
			elif search_type == '1':#search project by name of required skill:
				projs = ProjUtils.load_projs_by_skill(content)
			elif search_type == '2': # search user by name
				users = UserUtils.get_all_contribs_by_name(content)
			elif search_type == '3': # search user by skill
				users = UserUtils.get_users_by_skill(content)
			if search_type in ['2', '3']:
				return render_template('search.html', search_bar=search_bar, users=users)
			elif search_type in ['0', '1']:
				return render_template('search.html', search_bar=search_bar, projs=projs)
	return render_template('search.html', search_bar=search_bar)
	
@app.route('/signup', methods=['Get', 'POST'])
def signup():
	new_uid = 0
	form_signup = SignUp()
	if form_signup.validate_on_submit():
		UserUtils.create_user(FormUtils.load_form_signup())
		return render_template('signup_confirm.html')
	return render_template('signup.html', form=form_signup)
	
@app.route('/homepage', methods=['Get', 'POST'])
def homepage():
	new_proj = CreateProj()
	search_bar = SearchBar()
	if request.method == "POST":
		action = request.form['action']
		if action[0:6] == 'create' and new_proj.validate_on_submit():
			ProjUtils.create_proj(FormUtils.load_form_proj())
			Session.client.projs = ProjUtils.load_projs(Session.client.id, Session.client.perm)
			flash('Project was successfully created', 'error')
		elif action[0:6] == 'delete':
			ProjUtils.remove_proj(int(action[6:]))
			Session.client.projs = ProjUtils.load_projs(Session.client.id, Session.client.perm)
			flash('Project was successfully deleted', 'error')
	return render_template('homepage.html', new_proj=new_proj, user=Session.client, search_bar=search_bar)


@app.route('/project', methods=['Get', 'POST'])
def project():
	err = None
	if request.args.get('id'):
		Session.current_pid = int(request.args.get('id'))
	add_contrib = ReqUsername()
	new_task = AddTask()
	assign_task = ReqUsername()
	
	if request.method == 'POST':
		Session.refresh()
		action = request.form['action']
		if action[0:7] == 'deltask':
			TaskUtils.remove_task(Session.current_pid, int(action[7:]))
			flash("Task was successfully removed from project!", 'error')
		elif action[0:7] == 'addtask' and new_task.validate_on_submit():
				TaskUtils.create_task(FormUtils.load_form_task(Session.current_pid))
		elif action[0:7] == 'addcont' and add_contrib.validate_on_submit():
			status = ProjUtils.add_contrib(Session.current_pid, FormUtils.load_form_username())
			if status == 2:
				Session.errs.append("User is already a contributor to the project")
			elif status == 1:
				flash("User was successfully added as a contributor to the project", 'error')
			elif status == 0:
				Session.errs.append("Username does not exist")		
		elif action[0:7] == 'asstask' and assign_task.validate_on_submit():
			if not TaskUtils.assign(Session.current_pid, int(action[7:]), FormUtils.load_form_username()):
				Session.errs.append("User must be a contributor to the project to be assigned a task")
			else:
				flash("User was successfully assigned to the task")
		elif action[0:7] == 'rmcontr':
			ProjUtils.remove_contrib(Session.current_pid, int(action[7:]))
			print(int(action[7:]))
			flash("Contributor was successfully removed from project!", 'error')
		elif action[0:7] == 'altcomp':
			TaskUtils.update_status(Session.current_pid, int(action[7:]), True)
		elif action[0:7] == 'altprog':
			TaskUtils.update_status(Session.current_pid, int(action[7:]), False)
		return redirect(url_for('project'))
			
	return render_template('project.html', new_task=new_task, err=Session.errs, \
		contribs=ProjUtils.get_contribs(Session.current_pid), \
		proj=ProjUtils.get_proj(Session.current_pid, Session.client.projs), \
		tasks=TaskUtils.load_tasks(Session.current_pid), \
		owner=Session.client.perm, add_contrib=add_contrib, assign_task=assign_task)

if __name__ == "__main__":
	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('host', default='127.0.0.1')
	@click.argument('port', default=8111, type=int)
	def run(debug, threaded, host, port):
		print("running on %s:%d" % (host, port))
		app.run(host=host, port=port, debug=debug, threaded=threaded)
	run()