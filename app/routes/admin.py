from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import EventForm
from app.models import Event, db
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

def admin_required():
    return current_user.is_authenticated and current_user.role == 'admin'

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not admin_required():
        return redirect(url_for('events.home'))
    events = Event.query.all()
    return render_template('dashboard.html', events=events)

@admin_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if not admin_required():
        return redirect(url_for('events.home'))
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            time=form.time.data,
            capacity=form.capacity.data
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    return render_template('add_event.html', form=form)
