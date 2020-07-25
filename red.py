from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,PasswordField,SubmitField,BooleanField,SelectField,HiddenField
from wtforms.validators import DataRequired,InputRequired,Length,email,EqualTo,NumberRange,AnyOf


class RegistrationForm(FlaskForm):

    
    user_first_name = StringField('first name',validators=[InputRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_second_name = StringField('second name',validators=[InputRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_middle_name = StringField('middle name')
    user_email = StringField('email',validators=[InputRequired(), email()])
    user_password = PasswordField('password',validators=[InputRequired()])
    user_confirm_password = PasswordField('user_confirm password',validators=[InputRequired(), EqualTo('user_password',message='you entered diffirent password')])
    submit = SubmitField('SING UP')


class LoginForm(FlaskForm):

    user_email = StringField('email',validators=[InputRequired(), email()])
    user_password = PasswordField('password',validators=[InputRequired()])
    remember = BooleanField('REMEMBER ME')
    submit = SubmitField('Login')

class ResetForm(FlaskForm):
    user_first_name = StringField('first name',validators=[InputRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_second_name = StringField('second name',validators=[InputRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_email = StringField('email',validators=[InputRequired(), email()])
    new_password = PasswordField('new password',validators=[InputRequired()])
    submit = SubmitField('send')

class SubjectForm(FlaskForm):
    subjects = StringField('',validators=[InputRequired(), AnyOf(values=['mathematics','physics','chemistry','biology',
    'geography','english','economics','history','MATHEMATICS','PHYSICS','CHEMISTRY','BIOLOGY','GEOGRAPHY','ENGLISH',
    'ECONOMICS','HISTORY'] ,message='subject not found')])
    submit = SubmitField('send')


class AnswerForm(FlaskForm):
    subject_name = HiddenField('', render_kw={'id':'5675','value':'subject'})
    question_id = HiddenField('', render_kw={'id':'2342','value':'0'})
    answer = StringField('your answer',validators=[InputRequired(), AnyOf(values=['a','b','c','d'])])
    submit = SubmitField('submit', render_kw={"onclick": "questions_id()"})
  