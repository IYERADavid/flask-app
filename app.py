import os
import requests
import json
from flask import Flask ,render_template,url_for,request,redirect,flash,session,g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from operator import itemgetter
from forms import RegistrationForm,LoginForm,ResetForm,SubjectForm,AnswerForm  
import ast
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('FLASK_DB_URI')

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
    user_answers = db.Column(db.String(3), nullable=True)
    question = db.Column(db.String(1000000000000000000), nullable=False)

class Marks(db.Model):
    mark_id =  db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    questions_done = db.Column(db.Integer, nullable=False, default=0) 
    points = db.Column(db.Integer, nullable=False, default=0) 




@app.before_request
def before_request():
    g.user_id = None
    user_id = session.get('user_id',None)
    if user_id:
        g.user_id = user_id
@app.route('/logout',methods=['GET','POST'])
def logout():         
    session.pop('user_id',None)
    session.pop('subject_name',None)
    flash(message="YOU have successful logged out")
    return redirect(url_for('login'))

@app.route('/answer',methods=['POST'])
def answers():
    if not g.user_id:
        flash(message="You must Login or Signup")
        return redirect(url_for('login'))
    elif request.method == 'GET':
        flash(message="please select a subject")
        return redirect(url_for('subject_list'))        
    else:
        form = AnswerForm()
        current_question = Questions.query.filter_by(question_id=form.question_id.data).first()
        current_user_id = current_question.user_id
        if form.validate_on_submit() and current_user_id == session.get('user_id',None):
            user_answer= form.answer.data
            user_answer= user_answer.lower()
            subject = form.subject_name.data 
            question_id = form.question_id.data
            user_id = session.get('user_id',None)
            user_data = User.query.filter_by(id=user_id).first()
            user_name = user_data.user_second_name
            user_question_status = Marks.query.filter_by(user_id=user_id).first()
            if user_answer:
                user_question_status.questions_done += 1
                db.session.commit()
                question_done = user_question_status.questions_done
                user_completed_question = current_question
                user_completed_question.user_answers = user_answer
                db.session.commit()
                question_data = user_completed_question.question
                question_data = ast.literal_eval(question_data)
                user_answer = user_completed_question.user_answers
                correct_answer = question_data[u'answer']
                if correct_answer == user_answer:
                    update_marks = Marks.query.filter_by(user_id=user_id).first()
                    update_marks.points += 1
                    db.session.commit() 
                    score = update_marks.points
                else:
                    update_marks = Marks.query.filter_by(user_id=user_id).first()
                    score = update_marks.points
            flash(message="Answer for {} question ".format(subject))
            return render_template('answers.html',question_data=question_data,user_answer=user_answer,question_id=question_id,
            question_done=question_done,score=score,user_name=user_name)
        elif not form.validate_on_submit() and current_user_id == session.get('user_id',None):
            form = AnswerForm()
            question_id = form.question_id.data
            get_question = current_question
            question_data = get_question.question
            question_data = ast.literal_eval(question_data)
            error = "Your answer must be one of this a,b,c or d"
            flash(message="{}".format(error))
            return render_template('questions.html',question_data=question_data ,question_id=question_id ,form=form)
        else:
            flash(message="you must login again becouse we have dropped your session")
            return redirect(url_for('login'))


@app.route('/questions',methods=['GET','POST'])
def questions():
    if not g.user_id:
        flash(message="You must Login or Signup")
        return redirect(url_for('login'))
    elif request.method == 'GET' and not session.get('subject_name',None):
        flash(message="You must choose a subject to get a question")
        return redirect(url_for('subject_list'))
    else:    
        form = AnswerForm()

        subject_name = session.get('subject_name',None)
        aloc_base_url = "https://questions.aloc.com.ng/api/v2/q?subject="
        aloc_question_url = aloc_base_url + subject_name.lower()
        request_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'AccessToken': os.getenv('ALOC_ACCESS_KEY'),
        }

        try:
            req = requests.get(aloc_question_url, headers=request_headers )
        except requests.exceptions.ConnectionError:
            flash("Error connecting to the server. Please try again later.")
            return redirect(url_for('subject_list'))
        except requests.exceptions.Timeout:
            flash("The request timed out. Please check your connection and try again.")
            return redirect(url_for('subject_list'))
        except requests.exceptions.HTTPError as e:
            flash(f"HTTP error occurred: {e}")
            return redirect(url_for('subject_list'))
        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {e}")
            return redirect(url_for('subject_list'))
        except ValueError:
            flash("Invalid response received from the server.")
            return redirect(url_for('subject_list'))

        res = req.json()
        # this is the retrieved question from the Aloc api
        question_data = str(res['data'])
        user_id = session.get('user_id',None)
        question = Questions(user_id= user_id ,question= question_data)

        db.session.add(question)
        db.session.commit()

        question_id = question.question_id
        get_question = Questions.query.filter_by(question_id=question_id).first()
        question_data = get_question.question
        question_data = ast.literal_eval(question_data)

        flash(message="Welcome to {} question".format(subject_name))
        return render_template('questions.html',question_data=question_data ,question_id=question_id ,form=form,subject=subject_name)

@app.route('/subjects',methods=['GET','POST'])
def subject_list():
    if not g.user_id:
        flash(message="You must Login or Signup")
        return redirect(url_for('login'))
    else:
        form = SubjectForm()
        if form.validate_on_submit():
            session['subject_name'] = form.subjects.data
            return redirect(url_for('questions'))  
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
            flash(message='the email you entered already have an account here, Try another email')
            return redirect(url_for('register'))
        else:
            user_data = User(user_first_name= form.user_first_name.data,user_second_name= form.user_second_name.data,
            user_middle_name= form.user_middle_name.data,user_email=form.user_email.data,user_password=form.user_password.data)
            db.session.add(user_data)
            db.session.commit()
            flash(message='Account successful created for {}'.format(form.user_first_name.data))
            return redirect(url_for('login'))
    return render_template('register.html',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id',None)
    form = LoginForm()
    if form.validate_on_submit():
        verify_user = User.query.filter_by(user_email=form.user_email.data).first()
        if verify_user and verify_user.user_password == form.user_password.data:
            session['user_id']= verify_user.id
            user_id = verify_user.id
            user_mark_table = Marks.query.filter_by(user_id = user_id).first()
            if user_mark_table:
                return redirect(url_for('home_page'))
            else:
                create_user_mark_table = Marks(user_id = user_id , points = 0 )
                db.session.add(create_user_mark_table)
                db.session.commit()
                return redirect(url_for('home_page'))
        else:
            flash(message='your email or password is incorrect')
            return redirect(url_for('login')) 
    return render_template('login.html',form=form)
@app.route('/',methods=['GET','POST'])
def home_page():
    if not g.user_id:
        flash(message="You must Login or Signup")
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/home',methods=['GET','POST'])
def andrews_page():
    if request.method == 'GET':
        return render_template('index.html')

port = os.getenv('FLASK_PORT', 8080)  # Default to 8080 if not set
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(port))