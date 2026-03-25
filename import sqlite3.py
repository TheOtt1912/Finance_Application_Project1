import sqlite3
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

# -----Logging Setup-------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finance_app.log'),
    ]
)
logger = logging.getLogger(__name__)

console = Console()

# -----DB Setup-------
conn = sqlite3.connect('finance_app.db', isolation_level=None)
conn.execute('PRAGMA foreign_keys = ON')
logger.info('Database connection established.')

conn.execute('''
    CREATE TABLE IF NOT EXISTS people
    (name TEXT, people_id INTEGER PRIMARY KEY)
    STRICT
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS owingTransactions
    (amount REAL,
     people_id INTEGER,
     date_of_tx TEXT DEFAULT (datetime('now')) NOT NULL,
     status TEXT CHECK(status IN ('paid','not_paid','FORGIVEN')) NOT NULL,
     i_owe INTEGER CHECK(i_owe IN (0,1)) NOT NULL,
     FOREIGN KEY (people_id) REFERENCES people(people_id))
    STRICT
''')
logger.info('Tables verified/created.')


def print_menu():
    menu = Table.grid(padding=(0, 2))
    menu.add_column(style='bold yellow')
    menu.add_column(style='white')
    menu.add_row('[1]', 'Who do I owe?')
    menu.add_row('[2]', 'Who owes me?')
    menu.add_row('[3]', 'Total I owe')
    menu.add_row('[4]', 'Total owed to me')
    menu.add_row('[5]', 'Add new person')
    menu.add_row('[6]', 'List all people')
    menu.add_row('[7]', 'Add new transaction')
    menu.add_row('[Q]', 'Quit')
    console.print(Panel(menu, title='[bold green]💰 Owing Ledger[/bold green]', border_style='green', padding=(1, 4)))


def start_finance_app():
    while True:
        console.print()
        print_menu()
        option = Prompt.ask('[bold green]>[/bold green]')

        if option == '1':
            list_i_owe()
        elif option == '2':
            list_owe_me()
        elif option == '3':
            total_i_owe()
        elif option == '4':
            total_owed_to_me()
        elif option == '5':
            create_person()
        elif option == '6':
            list_all_people()
        elif option == '7':
            new_tx()
        elif option == 'q':
            console.print('\n[bold yellow]Bye 👋[/bold yellow]\n')
            break
        else:
            console.print('[red]Invalid option. Try again.[/red]')


def create_person():
    name = Prompt.ask('[bold]Name of person[/bold]')
    try:
        conn.execute('INSERT INTO people (name) VALUES (?)', (name,))
        console.print(f'[green]✓ {name} added successfully.[/green]')
        logger.info(f'Person added: {name}')
    except sqlite3.Error as e:
        console.print('[red]Something went wrong adding that person.[/red]')
        logger.error(f'Failed to add person "{name}": {e}')


def list_i_owe():
    try:
        cursor = conn.execute('''
            SELECT people.name, owingTransactions.amount
            FROM owingTransactions
            JOIN people ON people.people_id = owingTransactions.people_id
            WHERE owingTransactions.i_owe = 1 AND owingTransactions.status = 'not_paid'
        ''')
        results = cursor.fetchall()
        logger.info(f'list_i_owe returned {len(results)} rows.')
        if results:
            table = Table(box=box.SIMPLE_HEAVY, border_style='red')
            table.add_column('Person', style='white bold')
            table.add_column('Amount', style='red bold', justify='right')
            for name, amount in results:
                table.add_row(name, f'AED {amount:,.2f}')
            console.print(Panel(table, title='[bold red]You Owe[/bold red]', border_style='red'))
        else:
            console.print(Panel('[green]You owe nobody anything. Nice.[/green]', border_style='green'))
    except sqlite3.Error as e:
        logger.error(f'list_i_owe failed: {e}')


def list_owe_me():
    try:
        cursor = conn.execute('''
            SELECT people.name, owingTransactions.amount
            FROM owingTransactions
            JOIN people ON people.people_id = owingTransactions.people_id
            WHERE owingTransactions.i_owe = 0 AND owingTransactions.status = 'not_paid'
        ''')
        results = cursor.fetchall()
        logger.info(f'list_owe_me returned {len(results)} rows.')
        if results:
            table = Table(box=box.SIMPLE_HEAVY, border_style='green')
            table.add_column('Person', style='white bold')
            table.add_column('Amount', style='green bold', justify='right')
            for name, amount in results:
                table.add_row(name, f'AED {amount:,.2f}')
            console.print(Panel(table, title='[bold green]Owed To You[/bold green]', border_style='green'))
        else:
            console.print(Panel('[yellow]Nobody owes you anything.[/yellow]', border_style='yellow'))
    except sqlite3.Error as e:
        logger.error(f'list_owe_me failed: {e}')


def list_all_people():
    try:
        cursor = conn.execute('SELECT people_id, name FROM people')
        results = cursor.fetchall()
        logger.info(f'list_all_people returned {len(results)} rows.')
        if results:
            table = Table(box=box.SIMPLE_HEAVY, border_style='blue')
            table.add_column('#', style='yellow', justify='right')
            table.add_column('Name', style='white bold')
            table.add_column('ID', style='dim', justify='right')
            for i, (pid, name) in enumerate(results, start=1):
                table.add_row(str(i), name, str(pid))
            console.print(Panel(table, title='[bold blue]All People[/bold blue]', border_style='blue'))
        else:
            console.print(Panel('[yellow]No people added yet.[/yellow]', border_style='yellow'))
    except sqlite3.Error as e:
        logger.error(f'list_all_people failed: {e}')


def total_i_owe():
    try:
        cursor = conn.execute('''
            SELECT SUM(amount) FROM owingTransactions
            WHERE i_owe = 1 AND status = 'not_paid'
        ''')
        amount = cursor.fetchone()[0] or 0.0
        logger.info(f'total_i_owe: {amount}')
        console.print(Panel(f'[bold red]AED {amount:,.2f}[/bold red]', title='[red]Total You Owe[/red]', border_style='red'))
    except sqlite3.Error as e:
        logger.error(f'total_i_owe failed: {e}')


def total_owed_to_me():
    try:
        cursor = conn.execute('''
            SELECT SUM(amount) FROM owingTransactions
            WHERE i_owe = 0 AND status = 'not_paid'
        ''')
        amount = cursor.fetchone()[0] or 0.0
        logger.info(f'total_owed_to_me: {amount}')
        console.print(Panel(f'[bold green]AED {amount:,.2f}[/bold green]', title='[green]Total Owed To You[/green]', border_style='green'))
    except sqlite3.Error as e:
        logger.error(f'total_owed_to_me failed: {e}')


def new_i_owe_tx(person_id, amount):
    try:
        conn.execute('''
            INSERT INTO owingTransactions (amount, people_id, status, i_owe)
            VALUES (?, ?, ?, ?)
        ''', (amount, person_id, 'not_paid', 1))
        console.print('[green]✓ Transaction added.[/green]')
        logger.info(f'new_i_owe tx added: person_id={person_id}, amount={amount}')
    except sqlite3.Error as e:
        console.print('[red]Something went wrong adding that transaction.[/red]')
        logger.error(f'new_i_owe_tx failed: {e}')


def they_owe_tx(person_id, amount):
    try:
        conn.execute('''
            INSERT INTO owingTransactions (amount, people_id, status, i_owe)
            VALUES (?, ?, ?, ?)
        ''', (amount, person_id, 'not_paid', 0))
        console.print('[green]✓ Transaction added.[/green]')
        logger.info(f'they_owe tx added: person_id={person_id}, amount={amount}')
    except sqlite3.Error as e:
        console.print('[red]Something went wrong adding that transaction.[/red]')
        logger.error(f'they_owe_tx failed: {e}')


def new_tx():
    direction = Prompt.ask('[bold]0 = they owe you  |  1 = you owe them[/bold]', choices=['0', '1'])
    list_all_people()
    person_id = Prompt.ask('[bold]Enter Person ID[/bold]')
    amount = Prompt.ask('[bold]Amount (AED)[/bold]')

    if direction == '0':
        they_owe_tx(person_id, amount)
    else:
        new_i_owe_tx(person_id, amount)


if __name__ == '__main__':
    start_finance_app()