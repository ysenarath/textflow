"""Login view."""
from urllib.parse import urlparse, urljoin

from flask import redirect, flash, url_for, abort, request, Blueprint

from textflow import auth
from textflow.database import queries

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators


__all__ = [
    'bp',
    'LoginForm',
    'is_safe_url',
    'load_user',
    'unauthorized',
    'login',
    'logout',
]

bp = Blueprint('login', __name__)


class LoginForm(FlaskForm):
    """Login form.

    Attributes
    ----------
    username : StringField
        The username.
    password : PasswordField
        The password.
    """
    username = StringField(
        'Username', [
            validators.DataRequired(),
            validators.Length(min=4, max=25),
        ]
    )
    password = PasswordField(
        'Password', [
            validators.DataRequired(),
            validators.Length(min=8, max=25),
        ]
    )


def is_safe_url(target):
    """Checks whether target URL is safe.

    Parameters
    ----------
    target : str
        target URL.

    Returns
    -------
    bool
        True if target URL is safe, False otherwise.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@auth.login_manager.user_loader
def load_user(user_id):
    """Loads user.

    Parameters
    ----------
    user_id : int
        user ID.

    Returns
    -------
    User
        user
    """
    return queries.get_user(user_id=int(user_id))


@auth.login_manager.unauthorized_handler
def unauthorized():
    """Unauthorized handler.

    Returns
    -------
    redirect
        redirect to login page.
    """
    flash('You are not authorized to continue. Please login first.')
    return redirect(url_for('login.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login.

    Returns
    -------
    redirect
        Redirect the user to root page or target identified by next param.
    """
    target = request.args.get('next', '')
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    if request.method != 'POST':
        return redirect(url_for('index.index', login=True, target=target))
    form = LoginForm()
    if form.validate_on_submit():
        users = queries.filter_users(username=form.username.data)
        if len(users) <= 0 \
                or users[0] is None \
                or not users[0].verify_password(form.password.data):
            flash('Invalid username or password', 'error')
        else:
            user = users[0]
            # Login and validate the user.
            # user should be an instance of your `User` class
            auth.login_user(user)
            flash('Logged in successfully.', 'success')
            # login_user(user, remember=form.remember_me.data)
            # check whether it is safe to redirect to provide next
            if not is_safe_url(target):
                return abort(400)
            return redirect(target or url_for('index.index'))
    else:
        flash('Invalid username or password', 'error')
    return redirect(url_for('index.index', login=True, target=target))


@bp.route("/logout")
@auth.login_required
def logout():
    """Logout.

    Returns
    -------
    redirect
        Redirect the user to root page.
    """
    auth.logout_user()
    return redirect(url_for('index.index'))
