from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import TextAreaField, ValidationError, SelectField
from wtforms.validators import *
import phonenumbers as pn

	
class SignUp(FlaskForm):
	def is_valid_phone(form, field):
		if not pn.is_valid_number(pn.parse(field.data, "US")):
			raise ValidationError('Invalid Phone Number')
			
	name_syn = '^\s*[A-Za-z]+\s*$'
	fname = StringField('First Name', [Regexp(name_syn), InputRequired()])
	lname = StringField('Last Name', [Regexp(name_syn), InputRequired()])
	username = StringField('Username', [InputRequired()])
	password = PasswordField('Password', [InputRequired(), EqualTo('confirm_pass', 
				   message='Passwords do not match')])
	confirm_pass = PasswordField('Confirm Password', [InputRequired()])
	email = StringField('Email', [Email(), InputRequired()])
	phone = StringField('Phone', [InputRequired(), is_valid_phone])
	credent = TextAreaField('Credentials')
	role = SelectField('Role', choices=[('1', 'Owner'), ('0', 'Contributor')])
	submit = SubmitField('Sign Up');

class Login(FlaskForm):
	username = StringField('Username:', [InputRequired()])
	password = PasswordField('Password:', [InputRequired()])
	role = SelectField('Role:', choices=[('1', 'Owner'), ('0', 'Contributor')])
	submit = SubmitField('Sign In');
	
class CreateProj(FlaskForm):
	name = StringField('Project Name', [InputRequired()])
	description = TextAreaField('Description', [InputRequired()])
	src_link = StringField('source code link')
	image = StringField('Image Path')
	create = SubmitField('Create')
	