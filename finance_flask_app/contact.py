from finance_flask_app.db import get_db
from flask import( 
    Blueprint, flash, redirect, render_template, request, url_for
)


bp = Blueprint('contact',__name__,url_prefix=('/contact'))

@bp.route('/add', methods=('POST', 'GET'))
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        db = get_db()
        error = None

        if not name:
            error = 'Name required'
        
        if error is None:
            db.execute('''
                INSERT INTO contacts (name, email) VALUES (?,?)''',(name, email),
                )
            db.commit()
            return redirect(url_for('home'))
           #NEED AN ELSE part which says where to redirect after the thing is done
        flash(error)
    return render_template('contact/add.html')

def get_contacts():
    db = get_db()
    contact_list = db.execute('''SELECT id, name FROM contacts''').fetchall()
    
    return contact_list

