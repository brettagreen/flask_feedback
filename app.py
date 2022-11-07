"""Flask Feedback application."""

from forms import AddUserForm, AddLoginForm, AddFeedbackForm, PasswordResetRequestForm, PasswordResetForm
from flask import Flask, render_template, redirect, session, flash
from models import db, connect_db, User, Feedback, Token
from secrets import token_urlsafe
from emailz import send_pw_email

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "bush-did-911"

connect_db(app)
db.create_all()

@app.errorhandler(401)
def permissions_failure(e):
    return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET'])
def home():
    return redirect('/register')

@app.route('/verify_token/<string:token>', methods=['GET', 'POST'])
def verify_token(token):
    token = Token.query.get(token)
    form = PasswordResetForm()
    if form.validate_on_submit():
        pw1 = form.password1.data
        pw2 = form.password2.data

        if pw1 == pw2:
            hashed = User.get_pw_hash(pw1)
            user = User.get_user(token.username)
            user.password = hashed
            db.session.add(user)
            Token.query.filter_by(token=token.token).delete()
            db.session.commit()
            session['username'] = user.username
            if user.is_admin:
                session['admin'] = True
            else:
                session['admin'] = False
            
            return redirect(f'/users/{user.username}')

        else:
            flash("Passwords don't match. Please try again.")
            form = PasswordResetForm()
            user = token.username
            return render_template('index.html', title='reset your password', form_heading="Passwords must match", form=form)
            
    else:
        form = PasswordResetForm()
        user = token.username
        return render_template('index.html', title='reset your password', form_heading="Passwords must match", form=form)

@app.route('/pwreset', methods=['GET', 'POST'])
def request_reset():
    form = PasswordResetRequestForm()

    if form.validate_on_submit():

        email = form.email.data
        username = form.username.data
        token = token_urlsafe(32)
        new_token = Token(token=token, username=username)
        db.session.add(new_token)
        db.session.commit()
        
        url_token = f'http://localhost:5000/verify_token/{token}'
        send_pw_email(email, url_token)

        return redirect('/login')
    else:
        return render_template('index.html', title="request pw reset", 
                            form_heading="Provide your email. We will send you a link so you can reset your password.", form=form)

@app.route('/register', methods=['GET', 'POST'])
def all_cupcakes():
    form = AddUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        is_admin = False
        session['admin'] = is_admin

        hashed = User.get_pw_hash(password)

        new_user = User(username=username, password=hashed, email=email, first_name=first_name, last_name=last_name, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        return redirect(f'/users/{username}')
    else:
        return render_template('index.html', title="register your account", form_heading="Register your account!", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AddLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if User.check_pw(username, password):
            user = User.get_user(username)
            if user.is_admin:
                session['admin'] = True
            else:
                session['admin'] = False

            session['username'] = username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ["Bad name/password. Please try again."]
            return render_template('index.html', title="log in to your account", form_heading="Login to your account!", form=form,
                                    show_pw_reset=True)
    else:
        return render_template('index.html', title="log in to your account", form_heading="Login to your account!", form=form,
                                show_pw_reset=True)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username')
    if 'admin' in session:
        session.pop('admin')
    return redirect('/login')


@app.route('/users/<string:username>', methods=['GET'])
def user_info(username):
    if 'username' in session or 'admin' in session:
        if session['username'] == username or session['admin']:
            user = User.query.get_or_404(username)
            feedback = Feedback.query.filter_by(username=username).all()
            return render_template('user_info.html', user=user, feedback=feedback)
        else:
            flash('you do not have permission to perform that operation')
            return redirect(f"/users/{session['username']}")
    else:
        flash('you do not have permission to perform that operation')
        return redirect('/login')


@app.route('/users/<string:username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' in session or 'admin' in session:
        if session['username'] == username or session['admin']:
            session.pop('username')
            session.pop('admin')
            user = User.query.get_or_404(username)
            db.session.delete(user)
            db.session.commit()
            return redirect('/register')
        else:
            flash('you do not have permission to perform that operation')
            return redirect(f"/users/{session['username']}")
    else:
        flash('you do not have permission to perform that operation')
        return redirect('/login')


@app.route('/users/<string:username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' in session or 'admin' in session:
        if session['username'] == username or session['admin']:
            form = AddFeedbackForm()

            if form.validate_on_submit():
                title = form.title.data
                content = form.content.data
                feedback = Feedback(title=title, content=content, username=username)
                db.session.add(feedback)
                db.session.commit()

                return redirect(f'/users/{username}')
            else:
                return render_template('index.html', title="leave some feedback", form_heading="Add some feedback!",
                form=form, user=User.get_user(username)) 
        else:
            flash('you do not have permission to perform that operation')
            return redirect(f"/users/{session['username']}")
    else:
        flash('you do not have permission to perform that operation')
        return redirect('/login')


@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def update_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if 'username' in session or 'admin' in session:
        if session['username'] == feedback.username or session['admin']:
            form = AddFeedbackForm(obj=feedback)

            if form.validate_on_submit():
                feedback.title = form.title.data
                feedback.content = form.content.data
                db.session.add(feedback)
                db.session.commit()

                return redirect(f'/users/{feedback.username}')
            else:
                return render_template('index.html', title='edit feedback', form_heading="Edit your feedback",
                form=form, user=feedback.username)
        else:
            flash('you do not have permission to perform that operation')
            return redirect(f"/users/{session['username']}")
    else:
        flash('you do not have permission to perform that operation')
        return redirect('/login')
        

@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if 'username' in session or 'admin' in session:
        if session['username'] == feedback.username or session['admin']:
            db.session.delete(feedback)
            db.session.commit()
            return redirect(f'/users/{feedback.username}')
        else:
            flash('you do not have permission to perform that operation')
            return redirect(f"/users/{session['username']}")
    else:
        flash('you do not have permission to perform that operation')
        return redirect('/login')
