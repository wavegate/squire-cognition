from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm, DottestForm
from app.models import User, Test
from app.translate import translate
from app.main import bp
import sys


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    tests = current_user.followed_tests().paginate(
        page, current_app.config['TESTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=tests.next_num) \
        if tests.has_next else None
    prev_url = url_for('main.index', page=tests.prev_num) \
        if tests.has_prev else None
    return render_template('index.html', title=_('Home'),
                           tests=tests.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    tests = Test.query.order_by(Test.timestamp.desc()).paginate(
        page, current_app.config['TESTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=tests.next_num) \
        if tests.has_next else None
    prev_url = url_for('main.explore', page=tests.prev_num) \
        if tests.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           tests=tests.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    tests = user.tests.order_by(Test.timestamp.desc()).paginate(
        page, current_app.config['TESTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=tests.next_num) if tests.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=tests.prev_num) if tests.has_prev else None
    return render_template('user.html', user=user, tests=tests.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))

@bp.route('/delete_test/<int:test_id>')
@login_required
def delete_test(test_id):
    test = Test.query.get(test_id)
    if test.author == current_user:
        db.session.delete(test)
        db.session.commit()
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    tests, total = Test.search(g.search_form.q.data, page,
                               current_app.config['TESTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['TESTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), tests=tests,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/tests')
@login_required
def tests():
    return render_template('tests.html', title=_('Tests'))

@bp.route('/tests/example')
@login_required
def example_experiment():
    return render_template('tests/example.html', title=_('Example Experiment'))

@bp.route('/tests/magicseven')
@login_required
def magicseven():
    return render_template('tests/magicseven.html', title=_('Magic Number Seven'))

@bp.route('/tests/subitizing')
@login_required
def subitizing():
    return render_template('tests/subitizing.html', title=_('Subitizing'))

@bp.route('/tests/subitizing_run')
@login_required
def subitizing_run():
    return render_template('tests/subitizing_run.html', title=_('Subitizing - Run'))

@bp.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    test_name = request.form['test_name']
    #print(jsdata, file=sys.stderr)
    #with open('somefile.txt', 'a') as the_file:
    #    the_file.write(jsdata)
    test = Test(testname=test_name, score=jsdata, author=current_user)
    db.session.add(test)
    db.session.commit()
    return jsdata