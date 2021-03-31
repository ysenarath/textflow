""" Login View """

from urllib.parse import urlparse, urljoin

from flask import redirect, flash, url_for, render_template, abort, request, Blueprint

from textflow import services, auth
from textflow.view.forms import LoginForm

view = Blueprint('login_view', __name__)


def is_safe_url(target):
    """Checks whether URL target is safe.

    :param target: URL
    :return: whether target is safe or not
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth.login_manager.user_loader
def load_user(user_id):
    """Loads user from ID

    :param user_id: user_id
    :return: rendered template
    """
    return services.get_user(int(user_id))


@auth.login_manager.unauthorized_handler
def unauthorized():
    """Unauthorized redirection

    :return: rendered unauthorized
    """
    flash('You are not authorized to continue. Please login first.')
    return redirect(url_for('login_view.login'))


@view.route('/login', methods=['GET', 'POST'])
def login():
    """Login operation

    :return: rendered login form
    """
    target = request.args.get('next', '')
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            users = services.filter_users(username=form.username.data)
            if (len(users) <= 0) or (users[0] is None) or not users[0].verify_password(form.password.data):
                flash('Invalid login credentials', 'error')
            else:
                user = users[0]
                # Login and validate the user.
                # user should be an instance of your `User` class
                auth.login_user(user)
                flash('Logged in successfully', 'success')
                # login_user(user, remember=form.remember_me.data)
                # check whether it is safe to redirect to provide next
                if not is_safe_url(target):
                    return abort(400)
                return redirect(target or url_for('index_view.index'))
        else:
            flash('Invalid login credentials', 'error')
    return render_template('login.html', next=target, form=form)


@view.route("/logout")
@auth.login_required
def logout():
    """Logout

    :return: root page
    """
    auth.logout_user()
    return redirect('/')
