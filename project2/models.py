################################
 # Author: Michael Adams
 # Course: CS 1520
 # Last Edit: 3/23/18
################################

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	password = db.Column(db.String(80), nullable=False)
	user_type = db.Column(db.String(64), nullable=False)

	def __init__(self, username, password, user_type):
		self.username = username
		self.password = password
		self.user_type = user_type

	# tell Python how to print
	def __repr__(self):
		return '<User {}>'.format(self.username)

class Event(db.Model):
	event_id = db.Column(db.Integer, primary_key=True)
	customer_id = db.Column(db.Integer, nullable=False)
	name = db.Column(db.String(24), nullable=False)
	date = db.Column(db.String(24), nullable=False)
	staff1 = db.Column(db.String(24), default='_')
	staff2 = db.Column(db.String(24), default='_')
	staff3 = db.Column(db.String(24), default='_')
	
	# tell Python how to print
	def __repr__(self):
		return '<Event {}>'.format(self.date)