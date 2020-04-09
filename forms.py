from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, widgets
from wtforms_html5 import DateField
from wtforms import TextAreaField, ValidationError, SelectField
from wtforms.validators import *
from wtforms_html5 import DateRange
import phonenumbers as pn
from datetime import date

class SignUp(FlaskForm):
	FNAME_SZ = 30
	LNAME_SZ = 30
	EMAIL_SZ = 50
	UNM_SZ = 50
	PWD_SZ = 30
	CREDENT_SZ = 250
	MSG_FNM_SZ = 'First name should not exceed ' + str(FNAME_SZ) + ' characters'
	MSG_LNM_SZ = 'Last name should not exceed ' + str(LNAME_SZ) + ' characters'
	MSG_EMAIL_SZ = 'Email Address should not exceed ' + str(EMAIL_SZ) + ' characters'
	MSG_UNM_SZ = 'Username should not exceed ' + str(UNM_SZ) + ' characters'
	MSG_PWD_SZ = 'Password should not exceed ' + str(PWD_SZ) + ' characters'
	MSG_CREDENT_SZ = 'Credentials should not exceed ' + str(CREDENT_SZ) + ' characters'
	
	def is_valid_phone(form, field):
		if field.data != "" and not pn.is_valid_number(pn.parse(field.data, "US")):
			raise ValidationError('Invalid Phone Number')
			
	name_syn = '^\s*[A-Za-z]+\s*$'
	fname = StringField('First Name', [Regexp(name_syn), InputRequired(), \
		Length(min=0, max=FNAME_SZ, message=MSG_FNM_SZ)])
	lname = StringField('Last Name', [Regexp(name_syn), InputRequired(), \
		Length(min=0, max=LNAME_SZ, message=MSG_LNM_SZ)])
	username = StringField('Username', [InputRequired(), Length(min=0, max=UNM_SZ, message=MSG_UNM_SZ)])
	password = PasswordField('Password', [InputRequired(), EqualTo('confirm_pass', 
				   message='Passwords do not match'), Length(min=0, max=PWD_SZ, message=MSG_PWD_SZ)])
	confirm_pass = PasswordField('Confirm Password', [InputRequired()])
	email = StringField('Email', [Email(), InputRequired(), \
		Length(min=0, max=EMAIL_SZ, message=MSG_EMAIL_SZ)])
	phone = StringField('Phone', [is_valid_phone])
	credent = TextAreaField('Credentials', [Length(min=0, max=CREDENT_SZ, message=MSG_CREDENT_SZ)])
	role = SelectField('Role', choices=[('1', 'Owner'), ('0', 'Contributor')])
	submit = SubmitField('Sign Up')

class Login(FlaskForm):
	username = StringField('Username:', [InputRequired()])
	password = PasswordField('Password:', [InputRequired()])
	role = SelectField('Role:', choices=[('1', 'Owner'), ('0', 'Contributor')])
	
class CreateProj(FlaskForm):
	NM_SZ = 30
	DES_SZ = 500
	SRC_LINK_SZ = 200
	IMG_SZ = 100
	MSG_NM_SZ = 'Project name should not exceed ' + str(NM_SZ) + ' characters'
	MSG_DES_SZ = 'Project description should not exceed ' + str(DES_SZ) + ' characters'
	MSG_SRC_LINK_SZ = 'Source Code Link should not exceed ' + str(SRC_LINK_SZ) + ' characters'
	MSG_IMG_SZ = 'Image path should not exceed ' + str(IMG_SZ) + ' characters'
	
	name = StringField('Project Name', [InputRequired(), Length(min=0, max=NM_SZ, message=MSG_NM_SZ)])
	description = TextAreaField('Description', [InputRequired(), Length(min=0, max=DES_SZ, message=MSG_DES_SZ)])
	src_link = StringField('source code link', [Length(min=0, max=SRC_LINK_SZ, message=MSG_SRC_LINK_SZ)])
	image = StringField('Image Path', [Length(min=0, max=IMG_SZ, message=MSG_IMG_SZ)])

class SearchBar(FlaskForm):
	
	search_val = StringField('', render_kw={"placeholder": "Search"})
	search_by = SelectField('', choices=[('-1', 'Search by'), ('1', 'Skill name'), ('0', 'Project name')])
	#submit = SubmitField('Search')

class AddTask(FlaskForm):
	NM_SZ = 30
	SKILL_SZ = 20
	DES_SZ = 500
	MSG_NM_SZ = 'Task name should not exceed ' + str(NM_SZ) + ' characters'
	MSG_SKILL_SZ = 'Skill name should not exceed ' + str(SKILL_SZ) + ' characters'
	MSG_DES_SZ = 'Task description should not exceed ' + str(DES_SZ) + ' characters'
	
	name = StringField('Task Name', [InputRequired(), Length(min=0, max=NM_SZ, message=MSG_NM_SZ)])
	description = TextAreaField('Description', [InputRequired(), Length(min=0, max=DES_SZ, message=MSG_DES_SZ)])
	deadline = DateField(label='Deadline', format='%Y-%m-%d', validators=[InputRequired(), DateRange(date.today(), None)])
	skill = StringField('Required Skill', [InputRequired(), Length(min=0, max=SKILL_SZ, message=MSG_SKILL_SZ)])

class ReqUsername(FlaskForm):
	UNM_SZ = 50
	MSG_UNM_SZ = 'Username should not exceed ' + str(UNM_SZ) + ' characters'
	username = StringField('', [InputRequired(), Length(min=0, max=UNM_SZ, message=MSG_UNM_SZ)], \
		render_kw={"placeholder":"Username", "style":"width:15rem; margin-left:18px; display: inline-block;"})
