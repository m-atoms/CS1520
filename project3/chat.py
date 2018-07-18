################################
 # Author: Michael Adams
 # Course: CS 1520
 # Last Edit: 4/6/18
################################

# import required modules
import time
import os
import json
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack, jsonify
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import or_

# import db stuff
from models import db, User, Chatroom, Message

# create app as instance of flask class
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'development key'
app.config.from_object(__name__)
db.init_app(app)

# create db using "flask initdb"
@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()

# Convenience method to look up the id for a username
def get_user_id(username):
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

# Convenience method to look up the id for a chatroom
def get_chat_id(chat_name):
	rv = Chatroom.query.filter_by(chat_name=chat_name).first()
	return rv.chatroom_id if rv else None

# Convenience method to look up the id for a message
def get_message_id(text):
	rv = Message.query.filter_by(text=text).first()
	return rv.message_id if rv else None

# full event list for owner
def get_all_rooms():
	rv = Chatroom.query.order_by(Chatroom.chat_name).all()
	return rv if rv else [] #apparently you cant iterate on None

# get chatroom by chat_name
def get_chat_by_name(chat_name):
	rv = Chatroom.query.filter_by(chat_name=chat_name).first()
	return rv if rv else None

# get all messages for given chat room
def get_all_messages(chat_name):
	rv = Message.query.filter_by(chat_name=chat_name).all()
	return rv if rv else []

def check_availabilty(chat_name):
	rv = Chatroom.query.filter_by(chat_name=chat_name).first()
	return rv if rv else None

def format_datetime(timestamp):
	"""Format a timestamp for display."""
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.route('/')
@app.route('/index')
def index():
	rooms = get_all_rooms()

	# if user is signed in and goes to index, 
	if g.user:
		user = User.query.filter_by(user_id=g.user.user_id).first()
		user.current_room_id = -1
		db.session.commit()

	return render_template('index.html', rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	if g.user:
		return redirect(url_for('index'))
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
			if user.current_room_id != -1:
				return redirect(url_for('chat', chatroom_id=user.current_room_id))
			else:
				#flash(user.current_room_id)
				return redirect(url_for('index'))
	return render_template('login.html', error=error)

# user registration 
@app.route('/register', methods=['GET', 'POST'])
def register():
	# user registration
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'You have to enter a username'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'The username is already taken'
		else:
			db.session.add(User(request.form['username'], request.form['password'], -1))
			db.session.commit()
			#flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

# basic logout
@app.route('/logout')
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	curr_room = g.user.current_room_id
	session.pop('user_id', None)
	return redirect(url_for('chat', chatroom_id=curr_room))

@app.route('/chat/<chatroom_id>')
def chat(chatroom_id):
	error = None
	chatroom = Chatroom.query.get(chatroom_id)
	messages = get_all_messages(chatroom.chat_name)
	if g.user:
		g.user.current_room_id = chatroom_id
		user = User.query.filter_by(user_id=g.user.user_id).first()
		user.current_room_id = chatroom_id
		db.session.commit()
	return render_template('chat.html', chatroom=chatroom, messages=messages)

@app.route('/get_new_messages', methods=['POST'])
def get_new_messages():
	t = int(float(request.form['timestamp']) * 0.001)
	msgs = Message.query.filter_by(chat_name=request.form['chat_name']).all()
	
	for msg in msgs:
		if msg.pub_date > t:
			return jsonify({
				"author": msg.author,
				"chat_name": msg.chat_name,
				"text": msg.text,
				"pub_date": format_datetime(msg.pub_date)
				})
	return "null"

@app.route('/add_message', methods=['POST'])
def add_message():
	"""Registers a new message for the user."""
	if 'user_id' not in session:
		abort(401)
	if request.form['text']:
		new_msg = Message(request.form['author'], request.form['chat_name'], request.form['text'], int(time.time()))
		db.session.add(new_msg)
		db.session.commit()
	return jsonify({
			"author": new_msg.author,
			"chat_name": new_msg.chat_name,
			"text": new_msg.text,
			"pub_date": format_datetime(new_msg.pub_date)
		})

@app.route('/create_room', methods=['POST'])
def create_room():
	if check_availabilty(request.form['chat_name']):
		flash("Sorrry, that name is unavailable")
	else:
		db.session.add(Chatroom(chat_name=request.form['chat_name'], creator_id=request.form['creator_id']))
		db.session.commit()
	return redirect(url_for('index'))

@app.route('/leave')
def leave():
	return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
	db.session.delete(Chatroom.query.get(request.form['chatroom_id']))
	db.session.commit()
	return redirect(url_for('index'))

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime