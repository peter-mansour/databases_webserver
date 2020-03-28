import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, flash
from forms import *
from flask_bootstrap import Bootstrap
from queries import *
from tables import *
import random as rand
import click

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'phm2122'
Bootstrap(app)

DATABASEURI = "postgresql://phm2122:9813@35.231.103.173/proj1part2"
engine = create_engine(DATABASEURI)

user = User()
rand.seed(1)
MIN_PID = 1
MIN_UID = 1
MIN_TID = 1
MAX_TID = 99
MAX_PID = 999999999999
MAX_UID = 999999999999

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
	global user
	form_login = Login()
	err_msg = None
	if form_login.validate_on_submit():
		unm = request.form.get('username')
		pwd = request.form.get('password')
		perm = int(request.form.get('role'))
		if perm:
			cur = g.conn.execute(login_owner.format(unm=unm, pwd=pwd))
		else:
			cur = g.conn.execute(login_contrib.format(unm=unm, pwd=pwd))
		row = cur.first()
		if row:
			user.id = int(row['user_id'])
			user.fnm = row['first_name']
			user.perm = perm
			flash('Successfully logged in!', 'error')
			return redirect(url_for('homepage'))
		else:
			err_msg = "Username or Password are Incorrect"
	return render_template('index.html', form=form_login, err=err_msg)
	
@app.route('/signup', methods=['Get', 'POST'])
def signup():
	global user
	uids = []
	new_uid = 0
	form_signup = SignUp()
	if form_signup.validate_on_submit():
		fnm = request.form.get('fname')
		lnm = request.form.get('lname')
		unm = request.form.get('username')
		pwd = request.form.get('password')
		email = request.form.get('email')
		phone = request.form.get('phone')
		credent = request.form.get('credent')
		cur = g.conn.execute(get_all_uids)
		for row in cur:
			uids.append(int(row['user_id']))
		uid = gen_id(MIN_UID, MAX_UID, uids)
		if credent == "":
			credent = 'NULL'
		if phone == "":
			phone = 'NULL'
		g.conn.execute(add2person.format(fnm=fnm, lnm=lnm, uid=uid, email=email, \
			unm=unm, pwd=pwd, credent=credent, phone=phone))
		if request.form.get('role'):
			g.conn.execute(add2owner.format(uid=uid))
		else:
			g.conn.execute(add2contrib.format(uid=uid))
		return render_template('signup_confirm.html')
	return render_template('signup.html', form=form_signup)
	
@app.route('/homepage', methods=['Get', 'POST'])
def homepage():
	global user
	new_proj = CreateProj()
	search_bar = SearchBar()
	if request.method == "POST":
		action = request.form['action']
		if action[0:6] == 'create':
			print("in create proj")
			if new_proj.validate_on_submit():
				pids = []
				proj_nm = request.form.get('name')
				proj_desc = request.form.get('description')
				proj_src_link = request.form.get('src_link')
				proj_img = request.form.get('image')
				cur = g.conn.execute(get_all_pids)
				for row in cur:
					pids.append(int(row['proj_id']))
				g.conn.execute(add2proj.format(pid=gen_id(MIN_PID, MAX_PID, pids), oid=user.id, \
					des=proj_desc, src_link=proj_src_link, img=proj_img, nm=proj_nm))
		elif action[0:6] == 'delete':
			g.conn.execute(delete_proj.format(pid=int(action[6:])))
	
	if user.perm:
		cur = g.conn.execute(get_owner_projs.format(uid=user.id))
	else:
		cur = g.conn.execute(get_contrib_projs.format(uid=user.id))
	user.projs.clear()
	for row in cur:
		prog_result = g.conn.execute(get_progress.format(pid=int(row['proj_id'])))
		prog = prog_result.first()
		if not prog:
			overdue = 0
			perc_comp = 0
		else:
			overdue = int(prog['overdue_tasks'])
			perc_comp = int(prog['percent_complete'])
		user.projs.append(Project(int(row['proj_id']), row['proj_name'], row['description'], \
			row['src_code_link'], row['image_path'], overdue, perc_comp, row['owner_id']))
	return render_template('homepage.html', new_proj=new_proj, fnm=user.fnm, \
		projs=user.projs, owner=user.perm, search_bar=search_bar)

@app.route('/project', methods=['Get', 'POST'])
def project():
	global user
	err = None
	proj_id = int(request.args.get('id'))
	new_task = AddTask()
	new_contrib = AddContrib()
	
	if request.method == 'POST':
		action = request.form['action']
		if action[0:7] == 'deltask':
			g.conn.execute(delete_task.format(pid=proj_id, tid=int(action[7:])))
		elif action[0:7] == 'addtask':
			if new_task.validate_on_submit():
				tids = []
				task_nm = request.form.get('name')
				task_desc = request.form.get('description')
				task_deadline = request.form.get('deadline')
				required_skill = request.form.get('skill')
				cur = g.conn.execute(get_proj_tids.format(pid=proj_id))
				for row in cur:
					tids.append(int(row['task_id']))
				tid = gen_id(MIN_TID, MAX_TID, tids)
				g.conn.execute(add2task.format(tid=tid, deadline=task_deadline,\
					des=task_desc, is_comp=False, pid=proj_id, nm=task_nm))
				g.conn.execute(add2required_skills.format(tid=tid, pid=proj_id, skill=required_skill))
		elif action[0:7] == 'addcont':
			if new_contrib.validate_on_submit():
				cur = g.conn.execute(get_contrib_by_username.format(uid=request.form.get('username')))
				cid = cur.first()
				if cid:
					g.conn.execute(add_contribor.format(pid=proj_id, cid=cid))
				else:
					err = "Username does not exist"
					
	proj_contribs = []
	cur = g.conn.execute(get_proj_contribs.format(pid=proj_id))
	for row in cur:
		proj_contribs.append([row['last_name'], row['first_name']])
	tasks = []
	cur = g.conn.execute(get_tasks.format(pid=proj_id))
	for row in cur:
		contribs = g.conn.execute(get_task_contribs_by_username.format(pid=proj_id, tid=int(row['task_id'])))
		contributor = contribs.first()
		if contributor:
			task_contrib = contributor['username']
		else:
			task_contrib = ' '
		skills = g.conn.execute(get_task_skills.format(pid=proj_id, tid=int(row['task_id'])))
		skill = skills.first()
		tasks.append(Task(row['task_name'], int(row['task_id']), row['deadline'], \
			row['description'], row['is_complete'], int(row['proj_id']), task_contrib, skill['skill_name']))
			
	return render_template('project.html', new_task=new_task, err=err, contribs=proj_contribs,\
		proj=get_proj(proj_id, user.projs), tasks=tasks, tasks_x=tasks, owner=user.perm, new_contrib=new_contrib)

def gen_id(min, max, list):
	while True:
		new_n = rand.randrange(min, max)
		if new_n not in list:
			break
	return new_n

def get_proj(id, list):
	for p in list:
		if p.id == id:
			return p
	return None

if __name__ == "__main__":
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