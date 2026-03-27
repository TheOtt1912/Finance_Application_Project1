from finance_flask_app.db import get_db
from flask import( 
    Blueprint, render_template, request
)

bp = Blueprint('home',__name__)

@bp.route('/')
def home():
    db = get_db()
    i_owe_list = db.execute('''SELECT contacts.name,  owingTransactions.amount, owingTransactions.id, strftime('%d-%m-%Y', owingTransactions.date_of_tx) as date_of_tx
                    FROM owingTransactions
                    JOIN contacts ON contacts.id = owingTransactions.contact_id
                    WHERE owingTransactions.i_owe IS 1 AND owingTransactions.status IS 'not_paid';
                            ''').fetchall()
    
    they_owe_list = db.execute('''SELECT contacts.name,  owingTransactions.amount, owingTransactions.id, strftime('%d-%m-%Y', owingTransactions.date_of_tx) as date_of_tx
                    FROM owingTransactions
                    JOIN contacts ON contacts.id = owingTransactions.contact_id
                    WHERE owingTransactions.i_owe IS 0 AND owingTransactions.status IS 'not_paid';
                            ''').fetchall()
    total_owed = db.execute(''' SELECT SUM(amount) as total_sum FROM owingTransactions
                    WHERE i_owe IS 0 AND status IS 'not_paid'
                ''').fetchall()
    #AI REC - total i ower = sum(row['amount'] for row in i_owe_list)

    total_i_owe = db.execute(''' SELECT SUM(amount) as total_sum FROM owingTransactions
                    WHERE i_owe IS 1 AND status IS 'not_paid'
                ''').fetchall()

    return render_template('home.html',they_owe_list=they_owe_list,i_owe_list=i_owe_list, total_owed=total_owed, total_i_owe = total_i_owe)
