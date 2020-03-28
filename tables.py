class Project():
	def __init__(self, id, nm, des, src, img, overdue, perc_comp, oid):
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
	def __init__(self, nm, tid, dl, des, isComp, pid, contrib, skill):
		self.name = nm
		self.id = tid
		self.deadline = dl
		self.description = des
		self.is_complete = isComp
		self.proj_id = pid
		self.contributor = contrib
		self.skill = skill

class User:
	fnm = None
	id = None
	projs = []
	perm = None


