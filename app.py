from flask import Flask, render_template, request, redirect, url_for, flash, session
import datetime
import os

from serv import (create_account, check_login, make_post, add_to_group,
                  return_feed_for_user, rm_from_group, GROUPS, create_group, get_user_groups)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')


def get_current_user():
    return session.get('username')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def make_obj(**kwargs):
    return type('Obj', (), kwargs)()


@app.route('/')
def index():
    if session.get('username'):
        return redirect(url_for('feed'))
    return redirect(url_for('login'))


@app.route('/feed')
@login_required
def feed():
    user = get_current_user()
    return render_template(
        'feed.html',
        current_user=user,
        posts=return_feed_for_user(user),
        user_groups=get_user_groups(user),
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user, result = check_login(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('feed'))
        else:
            flash(result)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = create_account(username, password)
        if result == "Account created successfully.":
            return redirect(url_for('feed'))
        else:
            flash(result)
    return render_template('new_user.html')


@app.route('/group')
@login_required
def group():
    return render_template(
        'groups.html',
        current_user=get_current_user(),
        groups=GROUPS,
    )


@app.route('/about')
@login_required
def about():
    return render_template('about.html', current_user=get_current_user())


@app.route('/post', methods=['POST'])
@login_required
def create_post():
    group_id = request.form['group_id']
    result = make_post(author=get_current_user(), body=request.form['body'], group_id=group_id)
    if result != "Post created.":
        flash(result)
    return redirect(url_for('feed'))


@app.route('/admin/create_group', methods=['POST'])
@login_required
def admin_create_group():
    result = create_group(request.form['group_id'])
    add_to_group(get_current_user(), request.form['group_id'])
    flash(result)
    return redirect(url_for('group'))


@app.route('/admin/add_user', methods=['POST'])
@login_required
def admin_add_user():
    result = add_to_group(request.form['username'], request.form['group_id'])
    flash(result)
    return redirect(url_for('group'))


@app.route('/admin/remove_user', methods=['POST'])
@login_required
def admin_remove_user():
    result = rm_from_group(request.form['username'], request.form['group_id'])
    flash(result)
    return redirect(url_for('group'))


# Demo data
create_account("ciara", "password123")
create_account("alice", "mypassword789")
create_account("bob", "passw0rd321")    
create_group("general")
create_group("secret")
add_to_group("alice", "general")
add_to_group("bob", "general")
add_to_group("alice", "secret")
make_post(author="alice", body="Hello world!", group_id="general")
make_post(author="bob", body="This is a secure social media platform.", group_id="general")
make_post(author="alice", body="This is a secret message.", group_id="secret")


if __name__ == '__main__':
    app.run(debug=True)
