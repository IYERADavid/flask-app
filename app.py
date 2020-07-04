from flask import Flask ,render_template,url_for,request,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from operator import itemgetter
from red import RegistrationForm,LoginForm,ResetForm,SubjectForm,AnswerForm
import urllib2
import json  
import random
import ast



app = Flask(__name__)
app.config['SECRET_KEY'] ='DAVID'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_first_name = db.Column(db.String(20), nullable=False) 
    user_second_name = db.Column(db.String(20), nullable=False) 
    user_middle_name = db.Column(db.String(20), nullable=True) 
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    user_password = db.Column(db.String(60), nullable=False)  
    user_date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  
    question_time = db.Column(db.DateTime, default=datetime.utcnow)
    question = db.Column(db.String(1000000000000), nullable=False)

class Marks(db. Model):
    mark_id =  db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    questions_done = db.Column(db.Integer, nullable=False, default=0) 
    points = db.Column(db.Integer, nullable=False, default=0)   

url = "https://questions.aloc.ng/api/q/1?subject="


@app.route('/answer',methods=['GET','POST'])
def answers():
    form = AnswerForm()
    user_answer= form.answer.data
    subject = session.get('subject',None)
    user_id = session.get('user_id',None) 
    question_id = session.get("question_id",None)
    check_answer = Questions.query.filter_by(question_id=question_id).first()
    language = check_answer.question
    language = ast.literal_eval(language)
    update_questions = Marks.query.filter_by(user_id=user_id).first()
    update_questions.questions_done += 1
    db.session.commit()
    question_done = update_questions.questions_done  
    for item in language:
        answer = item[u'answer']
        if answer == user_answer:
            update_marks = Marks.query.filter_by(user_id=user_id).first()
            update_marks.points += 1
            db.session.commit() 
            score = update_marks.points
        else:
            update_marks = Marks.query.filter_by(user_id=user_id).first()
            score = update_marks.points

    flash(message="Answer for {} question ".format(subject))
    return render_template('answers.html',language=language,form=form,question_id=question_id,
    question_done=question_done,score=score)      


@app.route('/questions',methods=['GET','POST'])
def questions():
    form = AnswerForm()
    language = session.get("subject",None)
    language = language.lower()
    subject = session.get("subject",None)  
    json_obj = urllib2.urlopen(url + language)
    data = json.load(json_obj)
    language=data[u'data']
    # variable language contain list of question
    user_id = session.get('user_id',None)
    # user_id contain the id of the use who logged in
    language = str(language)
    question = Questions(user_id= user_id ,question= language)
    # i added user_id and list of question to database
    # i have set question_id to be primary key 
    db.session.add(question)
    db.session.commit()
    question_id = question.question_id
    print (question_id)
    get_question = Questions.query.filter_by(question_id=question_id).first()
    language = get_question.question
    language = ast.literal_eval(language)
    session['question_id'] = question_id
    for item in language:
        answer = item[u'answer']
        #print(answer)
    flash(message="welcome to {} question".format(subject))
    return render_template('questions.html',language=language ,question_id=question_id ,form=form)

@app.route('/subjects',methods=['GET','POST'])
def subject_list():
    form = SubjectForm()
    if form.validate_on_submit():
        session["subject"]= form.subjects.data
        return redirect(url_for('questions'))
    else:
        return render_template('subject_list.html',form=form)  
    return render_template('subject_list.html',form=form)


@app.route('/user_password',methods=['GET','POST'])
def reset_user_password():
    form = ResetForm()
    if form.validate_on_submit():
        form = ResetForm() 
        user_exist= User.query.filter_by(user_first_name= form.user_first_name.data).first()
        if user_exist and user_exist.user_second_name == form.user_second_name.data and user_exist.user_email == form.user_email.data:
            user_exist.user_password = form.new_password.data
            db.session.commit()
            flash(message="password successful changed for {}".format(form.user_first_name.data))
            return redirect(url_for('login'))
        else:
            flash(message="your first name,second name or email doesn't exist")
            return redirect(url_for('reset_user_password'))

    return render_template('reset_password.html',form=form)

@app.route('/signup',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        check_email = User.query.filter_by(user_email= form.user_email.data).first()
        if check_email:
            flash(message='the email you entered already have an account here')
            return redirect(url_for('register'))
        else:
            user_data = User(user_first_name= form.user_first_name.data,user_second_name= form.user_second_name.data,
            user_middle_name= form.user_middle_name.data,user_email=form.user_email.data,user_password=form.user_password.data)
            db.session.add(user_data)
            db.session.commit()
            flash(message='Account successful created for {}'.format(form.user_first_name.data))
            return redirect(url_for('login'))
    return render_template('register.html',title='signup',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        verify_user = User.query.filter_by(user_email=form.user_email.data).first()
        if verify_user and verify_user.user_password == form.user_password.data:
            session['user_id']= verify_user.id
            user_id = verify_user.id
            user_mark_table = Marks.query.filter_by(user_id = user_id).first()
            if user_mark_table:
                return redirect(url_for('subject_list'))
            else:
                create_user_mark_table = Marks(user_id = user_id , points = 0 )
                db.session.add(create_user_mark_table)
                db.session.commit()
                return redirect(url_for('subject_list'))
        else:
            flash(message='your email or password is incorrect')
            return redirect(url_for('login')) 
    return render_template('login.html',title='login',form=form)
@app.route('/',methods=['GET','POST'])
def home_page():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)    