
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "supersecretkey"   


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:9456@localhost:5432/crud_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  

with app.app_context():
    db.create_all()



@app.route('/')
def inde():
    users = data.query.all()
    return render_template('inde.html', users=users)

@app.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = data.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('create_user'))

        hashed_pw = generate_password_hash(password)

        try:
            new_user = data(name=name, email=email, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully!", "success")
            return redirect(url_for('inde'))
        except IntegrityError:
            db.session.rollback()
            flash("Error creating user.", "danger")
    
    return render_template('create.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user = data.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']

        if request.form['password']:  
            user.password = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash("User updated successfully!", "info")
        return redirect(url_for('inde'))
    return render_template('update.html', user=user)

@app.route('/delete/<int:id>')
def delete_user(id):
    user = data.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "warning")
    return redirect(url_for('inde'))

if __name__ == '__main__':
    app.run(debug=True)
