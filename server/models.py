from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nickname = db.Column(db.String(80))
    avatar = db.Column(db.String(200))
    token = db.Column(db.String(255), unique=True, nullable=True)
    token_expires = db.Column(db.DateTime, nullable=True)
    last_active_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'last_active_at': (self.last_active_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') if self.last_active_at else None
        }
    
    def generate_token(self):
        """生成新的token和过期时间"""
        self.token = secrets.token_urlsafe(32)
        self.token_expires = datetime.utcnow() + timedelta(hours=12)
        return self.token
    
    def is_token_valid(self):
        """检查token是否有效"""
        if not self.token or not self.token_expires:
            return False
        return datetime.utcnow() < self.token_expires
    
    def to_dict_with_token(self):
        """返回包含token的用户信息"""
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'last_active_at': (self.last_active_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') if self.last_active_at else None,
            'token': self.token,
            'token_expires': self.token_expires.strftime('%Y-%m-%d %H:%M:%S') if self.token_expires else None
        }

class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    type = db.Column(db.String(20)) # 'anniversary' or 'plan'
    details = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'type': self.type,
            'details': self.details,
            'user_id': self.user_id
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    images = db.Column(db.Text) # JSON string
    video = db.Column(db.String(200))
    mood = db.Column(db.String(20), default='normal') # 'normal', 'hug', 'want_hug', 'miss_you'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True, order_by="Comment.timestamp")
    user = db.relationship('User', backref='posts')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname,
            'user_avatar': self.user.avatar,
            'content': self.content,
            'images': self.images,
            'video': self.video,
            'mood': self.mood,
            'timestamp': (self.timestamp + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'likes': [like.user_id for like in self.likes],
            'comments': [c.to_dict() for c in self.comments]
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def to_dict(self):
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname,
            'user_avatar': self.user.avatar,
            'content': self.content,
            'reply_to_id': self.reply_to_id,
            'timestamp': (self.timestamp + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        }
        if self.reply_to_id:
            # Ideally we would fetch parent user nickname, but for simplicity let's rely on frontend or separate query if needed.
            # But wait, self.parent is available due to backref
            if self.parent:
                data['reply_to_nickname'] = self.parent.user.nickname
        return data

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.String(10), default='text') # 'text', 'image', 'video', 'voice'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'msg_type': self.msg_type,
            'timestamp': (self.timestamp + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            'sender_avatar': self.sender.avatar,
            'receiver_avatar': self.receiver.avatar
        }
