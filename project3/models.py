################################
 # Author: Michael Adams
 # Course: CS 1520
 # Last Edit: 4/6/18
################################

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False, unique=True)
	password = db.Column(db.String(80), nullable=False)
	current_room_id = db.Column(db.Integer, nullable=False)
	

	def __init__(self, username, password, current_room_id):
		self.username = username
		self.password = password
		self.current_room_id = current_room_id

	# tell Python how to print
	def __repr__(self):
		return '<User {}>'.format(self.username)

class Chatroom(db.Model):
	chatroom_id = db.Column(db.Integer, primary_key=True)
	chat_name = db.Column(db.String(24), nullable=False, unique=True)
	creator_id = db.Column(db.Integer, nullable=False)

	def __init__(self, chat_name, creator_id):
		self.chat_name = chat_name
		self.creator_id = creator_id

	# tell Python how to print
	def __repr__(self):
		return '<Chatroom Name {}>'.format(self.chat_name)

class Message(db.Model):
	messgae_id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(24), nullable=False)
	chat_name = db.Column(db.String(24), nullable=False)
	text = db.Column(db.String(200), nullable=False)
	pub_date = db.Column(db.Integer)

	def __init__(self, author, chat_name, text, pub_date):
		self.author = author
		self.chat_name = chat_name
		self.text = text
		self.pub_date = pub_date

	def __repr__(self):
		return '<Message {}'.format(self.messgae_id)