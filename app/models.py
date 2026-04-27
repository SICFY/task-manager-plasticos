from datetime import datetime
from flask_login import UserMixin
from . import db, bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='employee')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_tasks = db.relationship('Task', foreign_keys='Task.creator_id', backref='creator', lazy='dynamic')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id', backref='assignee', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email,
                'full_name': self.full_name, 'role': self.role, 'is_active': self.is_active,
                'created_at': self.created_at.isoformat()}

class Task(db.Model):
    __tablename__ = 'tasks'
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    priority = db.Column(db.String(10), default=PRIORITY_MEDIUM)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def is_completed(self):
        return self.status == self.STATUS_COMPLETED

    def is_overdue(self):
        if self.due_date and self.status != self.STATUS_COMPLETED:
            return datetime.utcnow() > self.due_date
        return False

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'description': self.description,
                'status': self.status, 'priority': self.priority,
                'due_date': self.due_date.isoformat() if self.due_date else None,
                'creator_id': self.creator_id, 'assignee_id': self.assignee_id,
                'is_overdue': self.is_overdue()}
