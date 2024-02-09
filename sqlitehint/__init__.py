"""
sqlitehint

Have a easier SQLite with helpful methods and readable syntax with **sqlitehint**.
This is designed to make working with sqlite3 better with more options.

sqlitehint is not an **ORM**. It can help you in type hinting (and with some other features, e.g. manage transactions).

Example::

    import sqlitehint

    class Movie(sqlitehint.RowModel):
        title: str
        year: int
        score: float

    conn = sqlitehint.connect("tutorial.db").tuning(journal_mode="WAL")

    with conn.context(begin=True) as ctx:
        ctx.execute("CREATE TABLE movie(title, year, score)")
        ctx.execute("INSERT INTO movie VALUES(?,?,?)", ('Python', 1975, 8.2))

    with conn.context(Movie) as ctx:
        ctx.selectall("SELECT * FROM movie")
        # Returns [Movie(title='Python', year=1975, score=8.2)]
"""

from .dbapi import RowModel
from .dbapi import TxContext
from .dbapi import Connection
from .dbapi import Cursor
from .dbapi import connect

from sqlite3.dbapi2 import (
    # Variables
    PARSE_COLNAMES as PARSE_COLNAMES,
    PARSE_DECLTYPES as PARSE_DECLTYPES,
    sqlite_version as sqlite_version,
    sqlite_version_info as sqlite_version_info,
    # Exceptions
    Error as Error,
    DataError as DataError,
    DatabaseError as DatabaseError,
    InternalError as InternalError,
    IntegrityError as IntegrityError,
    InterfaceError as InterfaceError,
    OperationalError as OperationalError,
    ProgrammingError as ProgrammingError,
    NotSupportedError as NotSupportedError,
)

__version__ = "1.0.19"

__all__ = [
    "RowModel",
    "Connection",
    "Cursor",
    "TxContext",
    "connect",
]
