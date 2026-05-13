from datetime import datetime
from functools import wraps
import json
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from models import CalendarEvent, Comment, Like, Message, Post, User, db


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI']:
    try:
        from sqlalchemy import create_engine

        uri = app.config['SQLALCHEMY_DATABASE_URI']
        if '/' in uri:
            base_uri, db_name = uri.rsplit('/', 1)
            engine = create_engine(base_uri)
            with engine.connect() as conn:
                conn.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                print(f"Database {db_name} ensured.")
    except Exception as exc:
        print(f"Warning: Could not create database. Error: {exc}")
        print("Please ensure database exists or check credentials.")


db.init_app(app)


def ensure_user_last_active_column():
    inspector = db.inspect(db.engine)
    columns = {column['name'] for column in inspector.get_columns('user')}
    if 'last_active_at' in columns:
        return

    statement = 'ALTER TABLE user ADD COLUMN last_active_at DATETIME'
    if db.engine.dialect.name != 'sqlite':
        statement = 'ALTER TABLE user ADD COLUMN last_active_at DATETIME NULL'

    db.session.execute(db.text(statement))
    db.session.commit()


def touch_user_activity(user):
    if not hasattr(user, 'last_active_at'):
        return
    try:
        user.last_active_at = datetime.utcnow()
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        app.logger.warning('Failed to update user activity: %s', exc)


def get_chat_meta(current_user):
    other_user = User.query.filter(User.id != current_user.id).order_by(User.id.asc()).first()
    if not other_user:
        return None

    last_active_at = getattr(other_user, 'last_active_at', None)
    is_online = bool(
        last_active_at
        and (datetime.utcnow() - last_active_at).total_seconds() <= 180
    )

    other_user_data = other_user.to_dict() if hasattr(other_user, 'to_dict') else {
        'id': other_user.id,
        'nickname': getattr(other_user, 'nickname', ''),
        'avatar': getattr(other_user, 'avatar', ''),
    }
    if 'last_active_at' not in other_user_data:
        other_user_data['last_active_at'] = None

    return {
        'other_user': other_user_data,
        'is_online': is_online,
    }


def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            token = request.headers.get('token')
        if not token:
            token = request.headers.get('X-Token')

        if not token:
            return jsonify({'code': 401, 'msg': 'Token required'}), 401

        if token.startswith('Bearer '):
            token = token[7:]

        user = User.query.filter_by(token=token).first()
        if not user or not user.is_token_valid():
            return jsonify({'code': 401, 'msg': 'Invalid or expired token'}), 401

        request.current_user = user
        touch_user_activity(user)
        return f(*args, **kwargs)

    return decorated_function


with app.app_context():
    db.create_all()
    ensure_user_last_active_column()

    if not User.query.first():
        user1 = User(
            username='user1',
            password='951106',
            nickname='星星住进太阳里',
            avatar='/static/avatar1.png',
        )
        user2 = User(
            username='user2',
            password='950812',
            nickname='太阳怀里有星星',
            avatar='/static/avatar2.png',
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({'code': 1, 'msg': 'Invalid credentials'})

    user.generate_token()
    user.last_active_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'code': 0, 'data': user.to_dict_with_token()})


@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    events = CalendarEvent.query.order_by(CalendarEvent.date).all()
    return jsonify({'code': 0, 'data': [event.to_dict() for event in events]})


@app.route('/api/calendar', methods=['POST'])
@require_token
def add_calendar():
    data = request.json
    event = CalendarEvent(
        title=data.get('title'),
        date=data.get('date'),
        type=data.get('type'),
        details=data.get('details'),
        user_id=request.current_user.id,
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify({'code': 0, 'data': [post.to_dict() for post in posts]})


@app.route('/api/posts', methods=['POST'])
@require_token
def add_post():
    data = request.json
    post = Post(
        user_id=request.current_user.id,
        content=data.get('content'),
        images=json.dumps(data.get('images', [])),
        video=data.get('video'),
        mood=data.get('mood', 'normal'),
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'code': 1, 'msg': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 1, 'msg': 'No selected file'})

    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = secure_filename(file.filename)
    filename = f"{int(datetime.now().timestamp())}_{filename}"
    file.save(os.path.join(upload_folder, filename))

    return jsonify({'code': 0, 'data': {'url': f"/static/uploads/{filename}"}})


@app.route('/api/posts/like', methods=['POST'])
@require_token
def like_post():
    data = request.json
    like = Like.query.filter_by(post_id=data.get('post_id'), user_id=request.current_user.id).first()
    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(post_id=data.get('post_id'), user_id=request.current_user.id))
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@app.route('/api/comments', methods=['POST'])
@require_token
def add_comment():
    data = request.json
    comment = Comment(
        post_id=data.get('post_id'),
        user_id=request.current_user.id,
        content=data.get('content'),
        reply_to_id=data.get('reply_to_id'),
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@app.route('/api/messages', methods=['GET'])
@require_token
def get_messages():
    messages = Message.query.order_by(Message.timestamp).all()
    chat_meta = None
    try:
        chat_meta = get_chat_meta(request.current_user)
    except Exception as exc:
        db.session.rollback()
        app.logger.warning('Failed to build chat meta: %s', exc)
    return jsonify({
        'code': 0,
        'data': [message.to_dict() for message in messages],
        'chat_meta': chat_meta,
    })


@app.route('/api/ping', methods=['GET'])
@require_token
def ping():
    return jsonify({'code': 0, 'msg': 'pong'})


@app.route('/api/messages', methods=['POST'])
@require_token
def send_message():
    data = request.json
    msg = Message(
        sender_id=request.current_user.id,
        receiver_id=data.get('receiver_id'),
        content=data.get('content'),
        msg_type=data.get('msg_type', 'text'),
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@app.route('/api/messages/delete', methods=['POST'])
@require_token
def delete_messages():
    data = request.json
    msg_ids = data.get('ids', [])
    if not msg_ids:
        return jsonify({'code': 1, 'msg': 'No ids provided'})

    Message.query.filter(Message.id.in_(msg_ids)).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


@app.route('/api/messages/recall', methods=['POST'])
@require_token
def recall_message():
    data = request.json
    msg_id = data.get('id')

    msg = Message.query.get(msg_id)
    if not msg:
        return jsonify({'code': 1, 'msg': 'Message not found'})
    if msg.sender_id != request.current_user.id:
        return jsonify({'code': 1, 'msg': 'Permission denied'})

    time_diff = datetime.utcnow() - msg.timestamp
    if time_diff.total_seconds() > 120:
        return jsonify({'code': 1, 'msg': '超过2分钟无法撤回'})

    db.session.delete(msg)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
