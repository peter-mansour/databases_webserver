from tables import *
from flask import g, request
from sqlalchemy import *
from queries import *
import random as rand
import sys

class Session:
	client = User()
	current_pid = None
	current_tid = None
	current_cid = None
	errs = []
	
	@staticmethod
	def refresh():
		Session.errs.clear()

class FormUtils:

	@staticmethod
	def load_form_signup():
		u = User()
		u.fnm = request.form.get('fname')
		u.lnm = request.form.get('lname')
		u.unm = request.form.get('username')
		u.pwd = request.form.get('password')
		u.email = request.form.get('email')
		u.phone = request.form.get('phone')
		u.credent = request.form.get('credent')
		u.perm = request.form.get('role')
		return u
	
	@staticmethod
	def load_form_username():
		return request.form.get('username')

	@staticmethod
	def load_form_proj():
		p = Project()
		p.name = request.form.get('name')
		p.description = request.form.get('description')
		p.src_code_link = request.form.get('src_link')
		p.image_path = request.form.get('image')
		return p

	@staticmethod
	def load_form_task(pid):
		t = Task()
		t.name = request.form.get('name')
		t.description = request.form.get('description')
		t.deadline = request.form.get('deadline')
		t.skill = request.form.get('skill')
		t.pid = pid
		return t
		
	@staticmethod
	def load_form_signin():
		u = User()
		u.unm = request.form.get('username')
		u.pwd = request.form.get('password')
		u.perm = int(request.form.get('role'))
		return u
	
	@staticmethod
	def load_form_evaluation():
		e = Eval()
		score = request.form.get('score')
		comment = request.form.get('comment')
		if score == '':
			e.score = None
		e.cmnt = None if comment == '' else comment
		e.score = None if score == '' else score
		return e

class ProjUtils:
	__MIN_PID = 1
	__MAX_PID = 99
	
	@staticmethod
	def create_proj(proj):
		pids = []
		cur = g.conn.execute(get_all_pids)
		for row in cur:
			pids.append(int(row['proj_id']))
		g.conn.execute(add2proj.format(pid=gen_id(ProjUtils.__MIN_PID, ProjUtils.__MAX_PID, pids), \
			oid=Session.client.id, des=proj.description, src_link=proj.src_code_link, \
			img=proj.image_path, nm=proj.name))

	@staticmethod
	def remove_proj(pid):
		g.conn.execute(delete_proj.format(pid=pid))
	
	@staticmethod
	def add_contrib(pid, cunm):
		proj_contribs = ProjUtils.get_contribs(pid)
		for user in proj_contribs:
			if cunm == user.unm:
				return 2
		all_contribs = UserUtils.get_users_by_perm(0)
		for user in all_contribs:
			if user.unm == cunm:
				g.conn.execute(add_contributor.format(pid=pid, cid=user.id))
				return 1
		return 0
	
	@staticmethod
	def remove_contrib(pid, cid):
		g.conn.execute(rm_contributor.format(pid=pid, cid=cid))
	
	@staticmethod
	def load_projs(uid, perm):
		list = []
		if perm:
			cur = g.conn.execute(get_owner_projs.format(uid=uid))
		else:
			cur = g.conn.execute(get_contrib_projs.format(uid=uid))
		for row in cur:
			prog_result = g.conn.execute(get_progress.format(pid=int(row['proj_id'])))
			prog = prog_result.first()
			if not prog:
				overdue = 0
				perc_comp = 0
			else:
				overdue = int(prog['overdue_tasks'])
				perc_comp = int(prog['percent_complete'])
			list.append(Project(int(row['proj_id']), row['proj_name'], row['description'], \
				row['src_code_link'], row['image_path'], overdue, perc_comp, row['owner_id']))
		return list
	
	@staticmethod
	def load_projs_by_name(name):
		projects = []
		cur = g.conn.execute(get_projs_by_name.format(name=name.lower()))
		for row in cur:
			prog_result = g.conn.execute(get_progress.format(pid=int(row['proj_id'])))
			prog = prog_result.first()
			if not prog:
				overdue = 0
				perc_comp = 0
			else:
				overdue = int(prog['overdue_tasks'])
				perc_comp = int(prog['percent_complete'])
			projects.append(Project(int(row['proj_id']), row['proj_name'], row['description'], \
				row['src_code_link'], row['image_path'], overdue, perc_comp, row['owner_id']))
		return projects

	@staticmethod
	def load_projs_by_skill(skillname):
		projects = []
		cur = g.conn.execute(get_projs_by_skill.format(skillname=skillname))
		for row in cur:
			prog_result = g.conn.execute(get_progress.format(pid=int(row['proj_id'])))
			prog = prog_result.first()
			if not prog:
				overdue = 0
				perc_comp = 0
			else:
				overdue = int(prog['overdue_tasks'])
				perc_comp = int(prog['percent_complete'])
			projects.append(Project(int(row['proj_id']), row['proj_name'], row['description'], \
				row['src_code_link'], row['image_path'], overdue, perc_comp, row['owner_id']))
		return projects

	@staticmethod
	def get_contribs(pid):
		list = []
		cur = g.conn.execute(get_proj_contribs.format(pid=pid))
		for row in cur:
			list.append(User(row['last_name'], row['first_name'], row['user_id'], row['username'], None, None))
		return list
	
	@staticmethod
	def get_proj(id, list):
		for p in list:
			if p.id == id:
				return p
		return None
	
class UserUtils:
	__MAX_UID = 999999999999
	__MIN_UID = 1
	
	@staticmethod
	def create_user(user):
		uids = []
		cur = g.conn.execute(get_all_uids)
		for row in cur:
			uids.append(int(row['user_id']))
		if user.credent == "":
			credent = 'NULL'
		if phone == "":
			phone = 'NULL'
		g.conn.execute(add2person.format(fnm=user.fnm, lnm=user.lnm, \
			uid=gen_id(UserUtils.__MIN_UID, UserUtils.__MAX_UID, uids), email=user.email, \
			unm=user.unm, pwd=user.pwd, credent=user.credent, phone=user.phone))
		if user.perm:
			g.conn.execute(add2owner.format(uid=uid))
		else:
			g.conn.execute(add2contrib.format(uid=uid))	
	
	@staticmethod
	def signin(user):
		if user.perm:
			cur = g.conn.execute(login_owner.format(unm=user.unm, pwd=user.pwd))
		else:
			cur = g.conn.execute(login_contrib.format(unm=user.unm, pwd=user.pwd))
		row = cur.first()
		if row:
			projs = ProjUtils.load_projs(int(row['user_id']), user.perm)
			return User(row['last_name'], row['first_name'], int(row['user_id']), row['username'], projs,\
				user.perm, row['password'], row['email'], row['phone_num'], row['credentials'])
		return None
	
	@staticmethod
	def get_users_by_perm(perm):
		users = []
		if perm:
			cur = g.conn.execute(get_all_owners)
		else:
			cur = g.conn.execute(get_all_contribs)
		for row in cur:
			users.append(User(row['last_name'], row['first_name'], row['user_id'], row['username'], None, None))
		return users

	@staticmethod
	def get_users_by_skill(skillname):
		users = []
		cur = g.conn.execute(get_all_person_by_skill.format(skillname=skillname))
		for row in cur:
			users.append(User(row['last_name'], row['first_name'], None, row['username'], email=row['email'], phone=row['phone_num']))
		return users

	@staticmethod
	def get_all_contribs_by_name(name):
		users = []
		cur = g.conn.execute(get_all_contribs_by_name.format(name=name))
		for row in cur:
			users.append(User(row['last_name'], row['first_name'], None, row['username'], email=row['email'], phone=row['phone_num']))
		return users
	
	@staticmethod
	def get_all_contrib_rating(contribs):
		ratings = {}
		for c in contribs:
			cur = g.conn.execute(get_rating.format(cid=c.id))
			row = cur.first()
			if row:
				ratings[row['contrib_id']] = row['avg_rating']
			else:
				ratings[c.id] = 0
		return ratings
		

class EvalUtils:
	__MIN_EID = 0
	__MAX_EID = 999999999999
	
	@staticmethod
	def get_all_eval_id():
		list = []
		all_ids = g.conn.execute(get_eval_ids)
		for id in all_ids:
			list.append(id['eval_id'])
		return list
	
	@staticmethod
	def add_eval(e, oid, cid):
		e.id = gen_id(EvalUtils.__MIN_EID, EvalUtils.__MAX_EID, EvalUtils.get_all_eval_id())
		comment = 'NULL'
		score = 0
		if e.cmnt:
			comment = e.cmnt
		if e.score:
			score = e.score
		if e.cmnt or e.score:
			g.conn.execute(eval_contrib.format(oid=oid, cid=cid, eid=e.id, cmnt=comment, score=score))
		
class TaskUtils:
	__MIN_TID = 1
	__MAX_TID = 99
	
	@staticmethod
	def create_task(task):
		tids = []	
		cur = g.conn.execute(get_proj_tids.format(pid=task.pid))
		for row in cur:
			tids.append(int(row['task_id']))
		task.id = gen_id(TaskUtils.__MIN_TID, TaskUtils.__MAX_TID, tids)
		g.conn.execute(add2task.format(tid=task.id, deadline=task.deadline, des=task.description, \
			is_comp=False, pid=task.pid, nm=task.name))
		g.conn.execute(add2required_skills.format(tid=task.id, pid=task.pid, skill=task.skill))
	
	@staticmethod
	def remove_task(pid, tid):
		g.conn.execute(delete_task.format(pid=pid, tid=tid))
	
	@staticmethod
	def assign(pid, tid, cunm):
		proj_contribs = ProjUtils.get_contribs(pid)
		for user in proj_contribs:
			if cunm == user.unm:
				g.conn.execute(assign_task.format(tid=tid, pid=pid, cid=user.id))
				return True
		return False
	
	@staticmethod
	def update_status(pid, tid, status):
		g.conn.execute(update_task_status.format(pid=pid, tid=tid, complete=status))
		
	@staticmethod
	def load_tasks(pid):
		tasks = []
		cur = g.conn.execute(get_tasks.format(pid=pid))
		for row in cur:
			contribs = g.conn.execute(get_task_contribs_username.format(pid=pid, tid=int(row['task_id'])))
			contributor = contribs.first()
			task_contrib = contributor['username'] if contributor else None
			skills = g.conn.execute(get_task_skills.format(pid=pid, tid=int(row['task_id'])))
			skill = skills.first()
			tasks.append(Task(row['task_name'], int(row['task_id']), row['deadline'], \
				row['description'], row['is_complete'], int(row['proj_id']), task_contrib, skill['skill_name']))
		return tasks

def gen_id(min, max, list):
	while True:
		new_n = rand.randrange(min, max)
		if new_n not in list:
			break
	return new_n