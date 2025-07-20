from flask import Blueprint, render_template, redirect, url_for, session, flash
from app.models import Event, db
from flask_login import login_required, current_user

events_bp = Blueprint('events', __name__)

@events_bp.route('/')
def home():
    events = Event.query.all()
    return render_template('home.html', events=events)

@events_bp.route('/event/<int:event_id>')
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user in event.attendees:
        flash("Already booked!")
    elif event.booked >= event.capacity:
        flash("No tickets available.")
    else:
        event.attendees.append(current_user)
        event.booked += 1
        db.session.commit()
        flash("Booking successful!")
    return redirect(url_for('events.home'))

@events_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
