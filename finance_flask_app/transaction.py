from finance_flask_app.db import get_db
from finance_flask_app.contact import get_contacts
from flask import( 
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('transaction',__name__,url_prefix='/transaction')

@bp.route('/add', methods=('POST', 'GET'))
def new_transaction():
    if request.method == 'POST':
        amount = request.form['amount']
        contact_id = request.form['contact_id']
        who_owes = request.form ['who_owes']
        db = get_db()
        error = None

        if not amount:
            error = 'Amount required.'
        elif not contact_id:
            error = 'Contact required'
        elif not who_owes:
            error = 'Who OWES WHO????!'
        
        if error is None:
            db.execute('''INSERT INTO owingTransactions (amount, contact_id, status, i_owe)  
                        VALUES (?, ?, ?, ?) ''', (amount, contact_id, 'not_paid', who_owes ),
                )
            db.commit()
            return redirect(url_for('home'))
        flash(error)
    contacts = get_contacts()
    return render_template('transaction/add.html', contacts=contacts)

@bp.route('/<int:id>/delete',methods=('POST',))
def delete_transaction(id):
    db = get_db()
    db.execute(''' DELETE FROM owingTransactions WHERE id = ? ''', (id,))
    db.commit()
    return(redirect(url_for('home.home')))

@bp.route('/<int:id>/paid',methods=('POST',))
def mark_as_paid(id):
    db = get_db()
    db.execute(''' UPDATE owingTransactions SET status = 'paid' WHERE id = ? ''', (id,))
    db.commit()
    return(redirect(url_for('home.home')))