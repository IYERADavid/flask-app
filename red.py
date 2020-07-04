from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,email,EqualTo,NumberRange,AnyOf


class RegistrationForm(FlaskForm):

    
    user_first_name = StringField('first name',validators=[DataRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_second_name = StringField('second name',validators=[DataRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_middle_name = StringField('middle name')
    user_email = StringField('email',validators=[DataRequired(), email()])
    user_password = PasswordField('password',validators=[DataRequired()])
    user_confirm_password = PasswordField('user_confirm password',validators=[DataRequired(), EqualTo('user_password',message='you entered diffirent password')])
    submit = SubmitField('SING UP')


class LoginForm(FlaskForm):

    user_email = StringField('email',validators=[DataRequired(), email()])
    user_password = PasswordField('password',validators=[DataRequired()])
    remember = BooleanField('REMEMBER ME')
    submit = SubmitField('Login')

class ResetForm(FlaskForm):
    user_first_name = StringField('first name',validators=[DataRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_second_name = StringField('second name',validators=[DataRequired(), Length(min=2, max=20,message='you name must have letters in range of 2 upto 20 ')])
    user_email = StringField('email',validators=[DataRequired(), email()])
    new_password = PasswordField('new password',validators=[DataRequired()])
    submit = SubmitField('send')

class SubjectForm(FlaskForm):
    subjects = StringField('',validators=[DataRequired(), AnyOf(values=['mathematics','physics','chemistry','biology',
    'geography','english','economics','history','MATHEMATICS','PHYSICS','CHEMISTRY','BIOLOGY','GEOGRAPHY','ENGLISH'
    'ECONOMICS','HISTORY'] ,message='subject not found')])
    submit = SubmitField('send')


class AnswerForm(FlaskForm):
    answer = StringField('your answer')
    submit = SubmitField('submit')
  