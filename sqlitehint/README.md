## SQLiteHint - SQLite helper

Have a easier SQLite with helpful methods and readable syntax with **sqlitehint**. This is designed to make working with sqlite3 better with more options.

sqlitehint is not an **ORM**. It can help you in type hinting (and with some other features, e.g. manage transactions).

> SQLite is a C library that provides a lightweight disk-based database that doesn’t require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language. Some applications can use SQLite for internal data storage. It’s also possible to prototype an application using SQLite and then port the code to a larger database such as PostgreSQL or Oracle.

**Features:**
- Full type hint
- Manage cursors easily
- Configure your database easily
- Start transaction easily
- Use locks for asynchronize applications.

**Installation**
```bash
pip3 install -U sqlitehint
```

**Content:**
- [tutorial](#tutorial)
- [reference](#reference)
- [how-to guide](#how-to-guide)

## Tutorial
In this tutorial, we're rewrite the [sqlite3 tutorial](https://docs.python.org/3/library/sqlite3.html#tutorial):

Use `sqlitehint.connect()` to create a connection to database *tutorial.db*:
```python
import sqlitehint
conn = sqlitehint.connect('tutorial.db')
```

We can use `tuning` method to configure the connection and database, for example we use it here to change [journal_mode](https://www.sqlite.org/pragma.html#pragma_journal_mode):
```python
conn = conn.tuning(journal_mode="WAL")
```

Like [sqlite3](https://docs.python.org/3/library/sqlite3.html#module-sqlite3) to execute SQL queries, we need a database cursor. In **sqlitehint**, we use `conn.context()` to create that:
```python
with conn.context() as ctx:
    # ...
```

For example, here we use it to create *movie* table and insert a row into it:
```python
with conn.context(autocommit=True) as ctx:
    ctx.execute("CREATE TABLE movie(title, year, score)")
    ctx.execute("INSERT INTO movie VALUES(?,?,?)", ('Python', 1975, 8.2))
```
We set **autocommit** to True, so the context will commit at the end and we don't need to call `conn.commit()`.

> [sqlite3](https://docs.python.org/3/library/sqlite3.html#module-sqlite3): Notice that `?` placeholders are used to bind data to the query. Always use placeholders instead of string formatting to bind Python values to SQL statements, to avoid SQL injection attacks

Now we can use `SELECT` query to verify that data was inserted.
So we can call `conn.context()` again or **use old context**.

> Notice that **sqlitehint** uses **sqlitehint.RowModel** instead of tuple.

Before creating context, we create an instance of *sqlitehint.RowModel* for *movie* table (*this is just for type hinting*).
```python
class Movie(sqlitehint.RowModel):
    title: str
    year: int
    score: float

with conn.context(Movie) as ctx:
    ctx.selectall("SELECT * FROM movie")
    # Returns [Movie(title='Python', year=1975, score=8.2)]

    # We can go normal way instead of using selectall:
    ctx.execute("SELECT * FROM movie")
    ctx.fetchall()
    # Returns [Movie(title='Python', year=1975, score=8.2)]
```

**Full Code**
```python
import sqlitehint

class Movie(sqlitehint.RowModel):
    title: str
    year: int
    score: float

conn = sqlitehint.connect("tutorial.db").tuning(journal_mode="WAL")

with conn.context(autocommit=True) as ctx:
    ctx.execute("CREATE TABLE movie(title, year, score)")
    ctx.execute("INSERT INTO movie VALUES(?,?,?)", ('Python', 1975, 8.2))

with conn.context(Movie) as ctx:
    ctx.selectall("SELECT * FROM movie")
    # Returns [Movie(title='Python', year=1975, score=8.2)]
```

## Reference
### sqlitehint.connect
Open a connection to an SQLite database.

**Parameters:**
- database (`StrOrBytesPath`): The path to the database file to be opened. You can pass ":memory:" to
                                create an SQLite database existing only in memory, and open a connection to it.

- timeout (`float`): How many seconds the connection should wait before raising an OperationalError when a table
                        is locked. If another connection opens a transaction to modify a table, that table will be
                        locked until the transaction is committed. Default five seconds.

- detect_types (`int`): Control whether and how data types not natively supported by SQLite are looked up to be
                        converted to Python types, using the converters registered with `register_converter()`.
                        Set it to any combination (using |, bitwise or) of PARSE_DECLTYPES and PARSE_COLNAMES
                        to enable this. Column names takes precedence over declared types if both flags are set.

- isolation_level (`str | None`): Control legacy transaction handling behaviour. See `Connection.isolation_level`
                                    and Transaction control via the isolation_level attribute for more information.
                                    Can be "DEFERRED" (default), "EXCLUSIVE" or "IMMEDIATE"; or None to disable
                                    opening transactions implicitly. Has no effect unless `Connection.autocommit`
                                    is set to LEGACY_TRANSACTION_CONTROL (the default).
- check_same_thread (`bool`): If True (default), ProgrammingError will be raised if the database connection is
                                used by a thread other than the one that created it. If False, the connection may
                                be accessed in multiple threads; write operations may need to be serialized by the
                                user to avoid data corruption.

- factory (`type[sqlite3.Connection]`): A custom subclass of Connection to create the connection with,
                                        if not the default Connection class.

- cached_statements (`int`): The number of statements that sqlite3 should internally cache for this connection,
                                to avoid parsing overhead. By default, 128 statements.

- uri (`bool`): If set to True, database is interpreted as a URI with a file path and an optional query string.
                The scheme part must be "file:", and the path can be relative or absolute.

- autocommit (`bool` - New in version 3.12): Control PEP 249 transaction handling behaviour. autocommit currently
                                                defaults to LEGACY_TRANSACTION_CONTROL. The default will change to
                                                False in a future Python release.

- context_block (`bool`): Specifies the context blocking situation. If True, the `context()` block is True on default,
                            And vice versa.

------
### sqlitehint.Connection
Each open SQLite database is represented by a `Connection` object, which is created using `sqlitehint.connect()`.

------
### sqlitehint.Connection.context
Creates a context and manage transactions.

**Parameters:**
- factory (`type | (Cursor, tuple) -> object | None`): Specifies the cursor row_factory, and this helps type hinting.

- begin (`bool`): If False, does not start a transaction, just returns the context.
                    If True, starts a transaction depends on isolation_level.

- autocommit (`bool`): If True, at the end of using context, it will automatically commits (or rollback)
                        the connection. (ignore this parameter if 'begin' is True)

- isolation_level (`str`): If begin=True, the isolation level will use for creating transaction.

- block (`bool`): (overrides the Connection.context_block) If True, and there is an another active transaction,
                    context will block the code until that be close. This is very helpful on multi-threads.

If begin is True and you are using `with` statement, the object will commit/rollback the transaction
at the exit

------
### sqlitehint.Connection.tuning
You can use it for change some connection settings and clean database to speed-up the database.

**Parameters:**
- vacuum (`bool`): If True, vacuums the database.

- journal_mode (`str`): If specified, changes database journal_mode.

- journal_size_limit (`str`): If specified, changes database journal_size_limit.

- synchronous (`str`): If specified, changes database synchronous.

**Example**
```python
>>> conn = sqlitehint.connect("test.db").tuning(vacuum=True, journal_mode="WAL", synchronous="NORMAL")
>>> conn.pragma("journal_mode")
('wal',)
>>> conn.pragma("synchronous")
(1,)
```

------
### sqlitehint.Connection.pragma
Executes the PRAGMA statements.

**Example**
```python
>>> conn.pragma("journal_mode", "wal")
>>> conn.pragma("journal_mode")
('wal',)
```

------
### sqlitehint.TxContext
Transaction context for managing transactions that returns by `Connection.context()`.

------
### sqlitehint.RowModel
An enchanced [sqlite3.Row](https://docs.python.org/3/library/sqlite3.html#sqlite3.Row) object.

You can use it as a subclass for typehinting like example.

## How-to guide
### How to use sqlitehint in threading?
**sqlitehint** provides a blocking mode protocol for threading and asynchronize applications.

If you want to use it, when calling `Connection.context()`, just set `block` parameter to True.

> **Threading Tip**: in threading, set journal_mode to 'WAL' and synchronous to 'NORMAL', that will improve database speed in threading.

For example:
```python
import sqlitehint
import threading

conn = sqlitehint.connect("threading.db", check_same_thread=False).tuning(journal_mode="WAL", synchronous="NORMAL")

with conn.context(autocommit=True) as ctx:
    ctx.execute("CREATE TABLE IF NOT EXISTS movie(title)")

def execute(n):
    with conn.context(block=True) as ctx:
        ctx.execute("INSERT INTO movie VALUES(?)", (str(n),))

threads = [threading.Thread(target=execute, args=(n,)) for n in range(10)]

for t in threads:
    t.start()
for t in threads:
    t.join()

# verify data
with conn.context() as ctx:
    assert (ctx.selectone("SELECT COUNT(*) FROM movie")[0]) == 10
```
