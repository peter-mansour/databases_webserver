class Project():
	def __init__(self, id=None, nm=None, des=None, src=None, \
		img=None, overdue=None, perc_comp=None, oid=None):
		self.id = id
		self.name = nm
		self.description = des
		self.src_code_link = src
		self.image_path = img
		self.progress = Progress(overdue, perc_comp)
		self.owner = oid

class Progress():
	def __init__(self, overdue, perc_comp):
		self.overdue_tasks = overdue
		self.percent_complete = perc_comp

class ContactInfo():
	def __init__(self, fn, ln, e, pn):
		self.first_name = fn
		self.last_name = ln
		self.email = e
		self.phone_num = pn

class Task():
	def __init__(self, nm=None, tid=None, dl=None, des=None, \
		isComp=None, pid=None, contrib=None, skill=None):
		self.name = nm
		self.id = tid
		self.deadline = dl
		self.description = des
		self.is_complete = isComp
		self.pid = pid
		self.contributor = contrib
		self.skill = skill

class User:
	def __init__(self, lnm=None, fnm=None, id=None, unm=None, \
		projs=[], perm=None, pwd=None, email=None, phone=None, credent=None):
		self.fnm = fnm
		self.lnm = lnm
		self.id = id
		self.unm = unm
		self.projs = projs
		self.perm = perm
		self.pwd = pwd
		self.email = email
		self.phone = phone
		self.credent = credent

class Eval:
	def __init__(self, cid=None, oid=None, score=None, id=None, cmnt=None):
		self.id = id
		self.cid = cid
		self.oid = oid
		self.score = score
		self.cmnt = cmnt
