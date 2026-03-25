DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS owingTransactions;

CREATE TABLE contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
) STRICT;

CREATE TABLE owingTransactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    contact_id INTEGER NOT NULL,
    date_of_tx TEXT DEFAULT (datetime('now')) NOT NULL,
    status TEXT CHECK(status IN ('paid','not_paid','FORGIVEN')) NOT NULL,
    i_owe INTEGER CHECK(i_owe IN (0,1)) NOT NULL, 
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
) STRICT;