#IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import random
import os

#BASE
app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greenup.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#OS
upload_avatar_folder = 'static/uploads'
file_names = {'png','jpg','jpeg','gif'}
app.config['upload_avatar_folder'] = upload_avatar_folder

#CLASS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    username = db.Column(db.String(100), nullable=False)
    last_completed = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, default='')
    avatar = db.Column(db.String(300), default='default_avatar.png')

class add_Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(100), nullable=True)
    edited = db.Column(db.Boolean, default=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))


#LISTS
TASK_LIST = [
    "Выбросить пластик в переработку",
    "Пройти пешком хотя бы 2 км",
    "Использовать многоразовую бутылку",
    "Выключить свет, выходя из комнаты",
    "Сократить использование бумаги",
    "Переработать батарейки",
    "Отказаться от одноразового пакета",
    "Посадить дерево или растение",
    "Собрать мусор в своём районе",
    "Не использовать пластик в течение дня",
    "Принести свои контейнеры в магазин или кафе",
    "Сократить время принятия душа",
    "Постирать вещи в холодной воде",
    "Отключить зарядки и электроприборы от сети",
    "Воспользоваться общественным транспортом",
    "Сдать стекло или бумагу на переработку",
    "Использовать тканевую сумку вместо пакета",
    "Не выбрасывать еду — доесть остатки",
    "Отдать ненужные вещи на благотворительность",
    "Провести день без пластика"
]

TIP_LIST = [
    "Начни день со стакана воды — меньше пластиковых бутылок.",
    "Выключай свет, выходя из комнаты — экономь энергию.",
    "Используй тканевую сумку вместо пакета.",
    "Собирай батарейки и лампочки отдельно — это важно.",
    "Пройди хотя бы 2 км пешком — меньше выбросов.",
    "Поливай растения остатками воды из бутылки.",
    "Сортируй мусор — начни хотя бы с бумаги и пластика.",
    "Бери в кафе свой многоразовый стакан.",
    "Не покупай воду в пластике — используй фильтр и бутылку.",
    "Откажись от одноразовой посуды сегодня.",
    "Посади дерево или цветок — это приятно и полезно.",
    "Дари ненужные вещи — меньше мусора, больше добра.",
    "Сократи время в душе на пару минут.",
    "Собери мусор в своём районе, даже если он чужой.",
    "Покупай местные продукты — меньше перевозок.",
    "Отложи телефон и прогуляйся по парку.",
    "Используй обе стороны листа бумаги.",
    "Покупай вещи не по моде, а на годы.",
    "Выключай зарядки из розетки после использования.",
    "Подари старую одежду благотворительности."
]

#ROUTES
@app.route('/')
def def_home_page():
    if 'user_id' in session:
        return redirect(url_for('def_login_page'))
    return render_template('homepage.html')


#REGISTER/LOGIN
@app.route('/register', methods=['GET', 'POST'])
def def_register_page():
    error=None
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            error = "Эта почта уже используется"
            return render_template('registerpage.html', error=error)
        elif User.query.filter_by(username=username).first():
            error = "Этот логин занят"
            return render_template('registerpage.html', error=error)
        else:
            new_user = User(email=email, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('def_login_page'))
        
    return render_template('registerpage.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def def_login_page():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email

            return redirect(url_for('def_dashboard'))

        else:
            error = "Неверный логин или пароль"
   
    return render_template('loginpage.html', error=error)

#DASHBOARD
@app.route('/dashboard')
def def_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('def_login_page'))

    today = date.today()
    random_tip = random.choice(TIP_LIST)

    if user.last_completed:
        delta = datetime.now() - user.last_completed
        if delta < timedelta(hours=2):
            tasks = Task.query.filter_by(user_id=user.id, date=user.last_completed.date()).all()
            remaining = timedelta(hours=2) -  delta
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            return render_template('dashboard.html', email=user.email, username=user.username, level=user.level, xp=user.xp, tasks=None, remaining_hours=hours, remaining_minutes=minutes, random_tip=random_tip)

    new_tasks = Task.query.filter_by(user_id=user.id, date=today).all()
    if not new_tasks:
        Task.query.filter_by(user_id=user.id).delete()
        for desc in random.sample(TASK_LIST, 5):
            task = Task(description=desc, user_id=user.id, date=today)
            db.session.add(task)
        db.session.commit()

    tasks = Task.query.filter_by(user_id=user.id, date=today).all()
    return render_template('dashboard.html', email=user.email, username=user.username,level=user.level, xp=user.xp, tasks=tasks, random_tip=random_tip)

@app.route('/complete-task/<int:task_id>', methods=['POST'])
def def_complete_task(task_id):
    task = Task.query.get(task_id)
    
    if task and not task.completed:
        task.completed = True
        user = User.query.get(task.user_id)
        
        xp_earned = random.randint(60,80)
        user.xp += xp_earned

        while user.xp >= 100:
            user.level += 1
            user.xp -= 100

        tasks = Task.query.filter_by(user_id=user.id, date=task.date).all()
        if all(i.completed for i in tasks):
            user.last_completed = datetime.now()

        db.session.commit()

    return redirect(url_for('def_dashboard'))

#PROFILE
@app.route('/profile')
def def_profile_page():
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))
    
    user = User.query.get(session['user_id'])
    friend_id_find = [i.friend_id for i in add_Friend.query.filter_by(user_id=user.id).all()]
    friends = User.query.filter(User.id.in_(friend_id_find)).all()

    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()

    return render_template('profile.html', user=user, friends=friends, posts=posts)

@app.route('/edit-profile', methods=['GET', 'POST'])
def def_edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    user = User.query.get(session['user_id'])
    error = None

    if request.method == 'POST':
        description = request.form.get('description', '')
        file = request.files.get('avatar')

        if description:
            user.description = description

        if file and file.filename != '':
            filename = file.filename 
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext in file_names:
                new_filename = f"user_{user.id}_{datetime.utcnow().timestamp()}.{ext}"
                file.save(os.path.join(app.config['upload_avatar_folder'], new_filename))
                user.avatar = new_filename
            else:
                error = "Недопустимый формат файла"

        if not error:
            db.session.commit()
            return redirect(url_for('def_profile_page'))

    return render_template('edit_profile.html', user=user, error=error)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    user = User.query.get(session['user_id'])

    description = request.form.get('description')
    if description:
        user.description = description

    avatar = request.files.get('avatar')
    if avatar and avatar.filename != '':
        filename = avatar.filename
        path = os.path.join(app.root_path, 'static/uploads', filename)
        avatar.save(path)
        user.avatar = filename

    db.session.commit()
    return redirect(url_for('def_profile_page'))

@app.route('/update_username', methods=['POST'])
def def_update_username():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    new_username = request.form.get('username')
    if new_username:
        user.username = new_username
        db.session.commit()
    return redirect(url_for('def_profile_page'))

@app.route('/update_description', methods=['POST'])
def def_update_description():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    new_description = request.form.get('description')
    if new_description:
        user.description = new_description
        db.session.commit()
    return redirect(url_for('def_profile_page'))

@app.route('/profile/<int:user_id>')
def def_view_other_profile(user_id):
    current_user_id = session.get('user_id')
    other_user = User.query.get_or_404(user_id)
    friend_id_find = [i.friend_id for i in add_Friend.query.filter_by(user_id=other_user.id).all()]
    friends = User.query.filter(User.id.in_(friend_id_find)).all()
    posts = other_user.posts
    is_friend = False
    pending_request = False
    if current_user_id:
        is_friend = add_Friend.query.filter_by(user_id=current_user_id, friend_id=user_id).first() is not None
        pending_request = FriendRequest.query.filter_by(sender_id=current_user_id, receiver_id=user_id, status='pending').first() is not None
    return render_template(
        'profile.html',
        user=other_user,
        friends=friends,
        posts=posts,
        is_other=True,
        is_friend=is_friend,
        pending_request=pending_request
    )

#FRIENDS
@app.route('/friends', methods=['GET','POST'])
def def_friends_page():
    if "user_id" not in session:
        return redirect(url_for('def_login_page'))

    user = User.query.get(session['user_id'])
    find_result = None

    if request.method == 'POST':
        username_temp = request.form['username_temp']
        find_result = User.query.filter_by(username=username_temp).first()

    friend_id_find = [i.friend_id for i in add_Friend.query.filter_by(user_id=user.id).all()]
    friends = User.query.filter(User.id.in_(friend_id_find)).all()

    requests = FriendRequest.query.filter_by(receiver_id=user.id, status='pending').all()
    for req in requests:
        req.sender = User.query.get(req.sender_id)

    return render_template('friends.html', user=user, friends=friends, find_result=find_result, requests=requests)

@app.route('/search_friend', methods=['POST'])
def search_friend():
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    username = request.form.get('username_temp')
    if not username:
        return redirect(url_for('def_profile_page'))

    user_found = User.query.filter_by(username=username).first()
    if user_found:
        return redirect(url_for('def_view_other_profile', user_id=user_found.id))
    else:
        error = 'Несуществующий пользователь'
        user = User.query.get(session['user_id'])
        friend_id_find = [i.friend_id for i in add_Friend.query.filter_by(user_id=user.id).all()]
        friends = User.query.filter(User.id.in_(friend_id_find)).all()
        requests = FriendRequest.query.filter_by(receiver_id=user.id, status='pending').all()
        for req in requests:
            req.sender = User.query.get(req.sender_id)
        return render_template('friends.html', user=user, friends=friends, find_result=None, requests=requests, error=error)

@app.route('/add-friend/<int:friend_id>', methods=["POST"])
def def_add_friend(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))
    
    user_id = session['user_id']
    if not add_Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first():
        db.session.add(add_Friend(user_id=user_id, friend_id=friend_id))
        db.session.commit()
    
    return redirect(url_for('def_friends_page'))

@app.route('/send-friend-request/<int:receiver_id>', methods=["POST"])
def send_friend_request(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    sender_id = session['user_id']

    existing_request = FriendRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id, status='pending').first()
    existing_friend = add_Friend.query.filter_by(user_id=sender_id, friend_id=receiver_id).first()

    if not existing_request and not existing_friend:
        new_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id)
        db.session.add(new_request)
        db.session.commit()

    return redirect(request.referrer or url_for('def_dashboard'))

@app.route('/respond-friend-request/<int:request_id>/<action>', methods=['POST'])
def respond_friend_request(request_id, action):
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    friend_request = FriendRequest.query.get(request_id)

    if friend_request and friend_request.receiver_id == session['user_id']:
        if action == 'accept':
            friend_request.status = 'accepted'

            db.session.add(add_Friend(user_id=friend_request.sender_id, friend_id=friend_request.receiver_id))
            db.session.add(add_Friend(user_id=friend_request.receiver_id, friend_id=friend_request.sender_id))
        elif action == 'decline':
            friend_request.status = 'declined'

        db.session.commit()

    return redirect(url_for('def_friends_page'))

@app.route('/remove-friend/<int:friend_id>', methods=['POST'])
def def_remove_friend(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))
    user_id = session['user_id']
    sort_friend = add_Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    reverse_friend = add_Friend.query.filter_by(user_id=friend_id, friend_id=user_id).first()
    if sort_friend:
        db.session.delete(sort_friend)
    if reverse_friend:
        db.session.delete(reverse_friend)
    db.session.commit()
    return redirect(url_for('def_friends_page'))

#POST
@app.route('/create_post', methods=['POST'])
def def_create_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])

    title = request.form.get('title')
    content = request.form.get('content')
    image_file = request.files.get('image')

    filename = None
    if image_file and image_file.filename != '':
        filename = image_file.filename
        image_path = os.path.join(app.root_path, 'static/uploads', filename)
        image_file.save(image_path)

    post = Post(
        user_id=user.id,
        title=title,
        content=content,
        image=filename,
        edited=False,
        likes=0
    )
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('def_profile_page'))

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def def_edit_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    post = Post.query.get_or_404(post_id)

    if post.user_id != session['user_id']:
        return redirect(url_for('def_profile_page'))

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        return redirect(url_for('def_profile_page'))

    return render_template('edit_post.html', post=post)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def def_delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))

    post = Post.query.get_or_404(post_id)

    if post.user_id != session['user_id']:
        return redirect(url_for('def_profile_page'))

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('def_profile_page'))


#COMMENT
@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('def_login_page'))
    content = request.form.get('comment_content')
    if content:
        comment = Comment(post_id=post_id, user_id=session['user_id'], content=content)
        db.session.add(comment)
        db.session.commit()
    return redirect(request.referrer or url_for('def_profile_page'))

@app.route('/edit_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if 'user_id' not in session or comment.user_id != session['user_id']:
        return redirect(url_for('def_login_page'))
    if request.method == 'POST':
        comment.content = request.form.get('comment_content')
        comment.edited = True
        db.session.commit()
        return redirect(url_for('def_view_other_profile', user_id=comment.post.user_id))
    return render_template('edit_comment.html', comment=comment)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if 'user_id' not in session or comment.user_id != session['user_id']:
        return redirect(url_for('def_login_page'))
    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer or url_for('def_profile_page'))

#LOGOUT
@app.route('/logout', methods=['POST'])
def def_logout():
    session.clear()
    return redirect(url_for('def_home_page'))

#START
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
