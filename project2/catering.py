################################
 # Author: Michael Adams
 # Course: CS 1520
 # Last Edit: 3/23/18
################################

# import required modules
import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import or_

# import db stuff
from models import db, User, Event

# create app as instance of flask class
app = Flask(__name__)

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'development key'
app.config.from_object(__name__)
db.init_app(app)

# create db using "flask initdb"
@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	db.session.add(User(username='owner', password='pass', user_type='owner'))
	db.session.commit()
	print(User.query.all())
	print('Initialized the database.')

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()

def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

# full event list for owner
def get_all_events():
	rv = Event.query.order_by(Event.date).all()
	return rv if rv else [] #apparently you cant iterate on None

# event list for customer
def get_customer_events(customer_id):
	rv = Event.query.filter_by(customer_id=customer_id).order_by(Event.date).all()
	return rv if rv else []

# event list of events staff is signed up for
def get_staff_events(user_id):
	rv = Event.query.filter(or_(Event.staff1==user_id, Event.staff2==user_id, Event.staff3==user_id))
	return rv if rv else []

def get_staff_openings(user_id):
	rv = Event.query.filter(~get_staff_events(user_id))

# check to make sure no other event is already scheduled
# if none, date is available
def check_availabilty(date):
	rv = Event.query.filter_by(date=date).first()
	return rv if rv else None

def format_datetime(timestamp):
	"""Format a timestamp for display."""
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	if g.user:
		return redirect(url_for('profile'))
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif user.password != request.form['password']:
			error = 'Invalid password'
		else:
			flash('You were logged in')
			session['user_id'] = user.user_id
			return redirect(url_for('profile'))
	return render_template('login.html', error=error)

# user registration 
@app.route('/register', methods=['GET', 'POST'])
def register():
	# owner can register users
	error = None
	if g.user and request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(request.form['username'], request.form['password'], user_type='staff'))
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	# customer registration
	elif request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(request.form['username'], request.form['password'], user_type='customer'))
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

# basic logout
@app.route('/logout')
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	session.pop('user_id', None)
	return redirect(url_for('index'))

# get appropriate event info and go to profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
	openings = None #this will only be set for staff 
	if g.user.user_type == 'owner':
		events = get_all_events()
	elif g.user.user_type == 'customer':
		events = get_customer_events(g.user.user_id)
	else:
		events = get_staff_events(g.user.username)
		openings = get_all_events() # i sort through this in profile
	return render_template('profile.html', events=events, openings=openings)	

# customer can add event
@app.route('/add_event', methods=['POST'])
def add_event():
	if check_availabilty(request.form['date']):
		flash("Sorrry, that date is unavailable.")
	else:
		db.session.add(Event(name=request.form['name'], date=request.form['date'], customer_id=request.form['customer_id']))
		db.session.commit()
		flash('Your event was created')
	events = get_customer_events(session['user_id'])
	return redirect(url_for('profile'))

# customer can delete event
@app.route('/delete_event', methods=['POST'])
def delete_event():
	db.session.delete(Event.query.filter_by(event_id=request.form['event_id']).first())
	db.session.commit()
	return redirect(url_for('profile'))

# sign up as staff1
@app.route('/sign_up1', methods=['POST'])
def sign_up1():
	temp = Event.query.filter_by(event_id=request.form['event_id']).first()
	temp.staff1 = request.form['staff1']
	db.session.commit()
	return redirect(url_for('profile'))

# sign up as staff2
@app.route('/sign_up2', methods=['POST'])
def sign_up2():
	temp = Event.query.filter_by(event_id=request.form['event_id']).first()
	temp.staff2 = request.form['staff2']
	db.session.commit()
	return redirect(url_for('profile'))

# sign up as staff3
@app.route('/sign_up3', methods=['POST'])
def sign_up3():
	temp = Event.query.filter_by(event_id=request.form['event_id']).first()
	temp.staff3 = request.form['staff3']
	db.session.commit()
	return redirect(url_for('profile'))

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime