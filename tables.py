class Proj():
	def __init__(self, des, src, img):
		#self.name = nm
		self.description = des
		self.src_code_link = src
		self.image_path = img

class Person():
	def __init__(self, fn, ln, uid, e, unm, pwd, cred, pn):
		self.first_name = fn
		self.last_name = ln
		self.user_id = uid
		self.email = e
		self.username = unm
		self.password = pwd
		self.credentials = cred
		self.phone_num = pn

class Task():
	def __init__(self, nm, tid, dl, des, isComp, pid):
		self.task_id = tid
		self.deadline = dl
		self.description = des
		self.isComplete = isComp
		self.proj_id = pid

