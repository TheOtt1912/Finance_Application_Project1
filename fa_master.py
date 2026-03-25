import sqlite3
import logging
#create a database of individuals

logging.basicConfig(
    level= logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler('finance_app.log'), #send to a file
        logging.StreamHandler() #show on terminal while app runs
    ] )
logger = logging.getLogger(__name__)

# -----DB Setup-------
conn = sqlite3.connect('finance_app.db', isolation_level=None)
conn.execute('PRAGMA foreign_keys = ON') #Necessary to enforce FK
logger.info('Database connection established.')

#Create Tables
#PEOPLE TABLE. Who I owe, or who may owe me
conn.execute('''
            CREATE TABLE IF NOT EXISTS people
            (name TEXT,
             people_id INTEGER PRIMARY KEY)
            STRICT
             '''
)
logger.info('Tables verified/created.')

# TRANSACTIONS between people and me for things I owe and am owed. 0 is FALSE so they owe. 1 will be TRUE so I owe.
conn.execute('''
            CREATE TABLE IF NOT EXISTS owingTransactions
            (amount REAL,
             people_id INTEGER,
             date_of_tx TEXT DEFAULT (datetime('now')) NOT NULL,
             status TEXT CHECK(status IN ('paid','not_paid','FORGIVEN')) NOT NULL,
             i_owe INTEGER CHECK(i_owe IN (0,1)) NOT NULL, 
             FOREIGN KEY (people_id) REFERENCES people(people_id)
             )
             STRICT
'''
)

#main finance app on/off, and add, and view txs
def start_finance_app():
    while True:
        print('''Hi, welcome to the owing ledger app!
            Menu:
            Who do I owe? Enter 1
            Who owes me? Enter 2
            Total I owe? Enter 3
            Total owed to me? Enter 4
            Add new person. Enter 5
            List all peeps. Enter 6 
            Add new transaction. Enter 7
            Quit. Enter q
              ''')
        option = input('>')
        
        if option == str(1):
            list_i_owe()
        elif option == str(2):
            list_owe_me()
        elif option == str(3):
            total_i_owe()
        elif option == str(4):
            total_owed_to_me()
        elif option == str(5):
            create_person()
        elif option == str(6):
            list_all_people()
        elif option == str(7):
            new_tx()
        elif option == 'q':
            print('Bye')
            break
        else:
            print('Please enter a valid option.')
            continue


def create_person():
    print('Enter name of person')
    p = input('>')
    try:
        conn.execute('''
                    INSERT INTO people (name) VALUES (?)''',(p,))
        print(p + ' successfully added!')
        logger.info(f'Person added: {p}')
    except sqlite3.Error as e:
        logger.error(f'Failed to add person "{p}": {e}')
        print('Something went wrong adding that person.')

def list_i_owe():
    try:
        cursor = conn.execute('''SELECT people.name,  owingTransactions.amount
                    FROM owingTransactions
                    JOIN people ON people.people_id = owingTransactions.people_id
                    WHERE owingTransactions.i_owe IS 1 AND owingTransactions.status IS 'not_paid';''')
        results = cursor.fetchall()
        logger.info(f'list_i_owe returned {len(results)} rows.')
        if results:
            for name, amount in results:
                print(f' {name}: AED{amount}')
        else:
            print('You owe nobody anything. Nice')
    except sqlite3.Error as e:
        logger.error(f'list_i_owe failed: {e}')

def list_owe_me():
    try:
        cursor = conn.execute('''SELECT people.name,  owingTransactions.amount
                    FROM owingTransactions
                    JOIN people ON people.people_id = owingTransactions.people_id
                    WHERE owingTransactions.i_owe IS 0 AND owingTransactions.status IS 'not_paid';''')
        results = cursor.fetchall()
        logger.info(f'list_owe_me returned {len(results)} rows')
        if results:
            for name, amount in results:
                print(f'{name}: AED{amount}')
        else:
            print('Nobody owes you shiiiit')
    
    except sqlite3.Error as e:
        logger.error(f'list_owe_me failed: {e}')

def list_all_people():
    try:
        cursor = conn.execute('''SELECT name FROM people''')
        results = cursor.fetchall()
        logger.info(f'list_all_people returned {len(results)} rows')
        
        if results:
            x = 1
            for name, in results:
                print(f' {x} - {name}')
                x += 1

    except sqlite3.Error as e:
        logger.error(f'list_all_people failed: {e}')

def total_i_owe():
    try:
        cursor = conn.execute(''' SELECT SUM(amount) as total_sum FROM owingTransactions
    WHERE i_owe IS 1 AND status IS 'not_paid' '''
        )
        results = cursor.fetchall()
        logger.info(f'total_i_owe returned')
        if results:
            for amount, in results:
                print(f' TOTAL I OWE: {amount}')

    except sqlite3.Error as e:
        logger.error(f'total_i_owe failed: {e}')

def total_owed_to_me():
    try:
        cursor = conn.execute(''' SELECT SUM(amount) as total_sum FROM owingTransactions
    WHERE i_owe IS 0 AND status IS 'not_paid' '''
        )
        results = cursor.fetchall()
        logger.info(f'total_owed_to_me returned')
        if results:
            for amount, in results:
                print(f' TOTAL OWED TO ME: {amount}')
    
    except sqlite3.Error as e:
        logger.error(f'total_owed_to_me failed: {e}')

def new_i_owe_tx(person_id, amount):
    try:
        conn.execute('''
                    INSERT INTO owingTransactions (amount, people_id, status, i_owe)  VALUES (?, ?, ?, ?) ''', (amount, person_id, 'not_paid', 1 )
    )
        print('Tx successfuly added')
        logger.info(f'new_i_owe_tx added')
    except sqlite3.Error as e:
        logger.error(f'new_i_owe_tx failed: {e}')
        print('Something went wrong adding that transaction.')

def they_owe_tx(person_id, amount):
    try:
        conn.execute('''
                    INSERT INTO owingTransactions (amount, people_id, status, i_owe)  VALUES (?, ?, ?, ?) ''', (amount, person_id, 'not_paid', 0 )
    )
        print('Tx successfuly added')
        logger.info(f'they_owe_tx added')
    except sqlite3.Error as e:
        logger.error(f'they_owe_tx failed: {e}')

def new_tx():
    while True:
        print('Enter 0 if you are owed money, or 1 if you owe money. Enter b to return to main menu')
        who_owes = input('>')
        if who_owes == str(0):
            print('Who owes you? ID of person.')
            person_id = input('>')
            print('How much do they owe you?')
            amount = input('>')
            they_owe_tx(person_id, amount)
        elif who_owes == str(1):
            print('Who do you owe? ID of person.')
            person_id = input('>')
            print('How much do you owe them?')
            amount = input('>')
            new_i_owe_tx(person_id, amount)
        elif who_owes == 'b':
            break
        else:
            print('invalid option')
            continue

def mark_tx_paid(tx_id):
    try:
        conn.execute('''
                     UPDATE owingTransactions
                     SET status = 'paid'
                     WHERE ROWID = (?)
                     ''', (str(tx_id,))
                     )
        logger.info(f'tx{tx_id}_successfully changed to paid')
    except sqlite3.Error as e:
        logger.error(f'Could not change tx to paid: {e}')

def mark_tx_forgiven(tx_id):
    try:
        conn.execute('''
                     UPDATE owingTransactions
                     SET status = 'FORGIVEN'
                     WHERE ROWID = (?)
                     ''', (str(tx_id,))
                     )
        logger.info(f'tx{tx_id}_successfully changed to FORGIVEN')
    except sqlite3.Error as e:
        logger.error(f'Could not change tx to FORGIVEN: {e}')



if __name__ == '__main__':
    start_finance_app()

#total_i_owe()
#total_owed_to_me()
#list_i_owe()
#list_owe_me()
#new_i_owe_tx(2,90)
#they_owe_tx (2,16000)