""" Login View """

from flask import redirect, flash, url_for, render_template, abort, request, Blueprint
from flask_login import login_required, logout_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

from textflow import services
from textflow.login import is_safe_url, login_manager

view = Blueprint('login_view', __name__)


@login_manager.user_loader
def load_user(user_id):
    """ Loads user from ID

    :param user_id: user_id
    :return: rendered template
    """
    return services.get_user(int(user_id))


class LoginForm(FlaskForm):
    """ LoginForm """
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=8, max=25)])


def login_form():
    """ Creates and returns login form

    :return: New LoginForm
    """
    return LoginForm()


@view.route('/login', methods=['GET', 'POST'])
def login():
    """ Login operation

    :return: rendered login form
    """
    errors = []
    target = request.args.get('next', '')
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = login_form()
    if form.validate_on_submit():
        users = services.filter_users(username=form.username.data)
        if len(users) < 0:
            errors.append('User not found. Please check your username and retry again.')
            return render_template('login.html', next=target, form=form, errors=errors)
        user = users[0]
        #
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login_view.login'))
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)
        flash('Logged in successfully.')
        # login_user(user, remember=form.remember_me.data)
        # check whether it is safe to redirect to provide next
        if not is_safe_url(target):
            return abort(400)
        return redirect(target or url_for('index_view.index'))
    return render_template('login.html', next=target, form=form)


@view.route("/logout")
@login_required
def logout():
    """ Logout

    :return: root page
    """
    logout_user()
    return redirect('/')


@login_manager.unauthorized_handler
def unauthorized():
    """ unauthorized redirection

    :return: rendered unauthorized
    """
    flash('You are not authorized to continue. Please login first.')
    return redirect(url_for('login_view.login'))
