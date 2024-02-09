from _typeshed import StrOrBytesPath
import sqlite3
import typing
import _thread
import sys

_Parameters = typing.Union[typing.Iterable, typing.Mapping[str, typing.Any]]
_JournalMode = typing.Literal["WAL", "OFF", "MEMORY", "PERSIST", "TRUNCATE", "DELETE"]
_Synchronous = typing.Literal["OFF", "NORMAL", "FULL", "EXTRA"]
_IsolationLevel = typing.Literal["DEFERRED", "EXCLUSIVE", "IMMEDIATE"]

class RowModel(sqlite3.Row):
    """
    A `RowModel` instance serves as a highly optimized row_factory for `Connection` objects.
    It supports iteration, equality testing, len(), and mapping access by column name and index.

    Two Row objects compare equal if they have identical column names and values.

    You can use it as a subclass for typehinting.
    """

    __slots__: tuple

    def __init_subclass__(cls) -> None: ...
    def __getattr__(self, __name: str) -> typing.Any: ...
    def __repr__(self) -> str: ...

_TT = typing.TypeVar("_TT")

class Cursor(sqlite3.Cursor, typing.Generic[_TT]):
    """
    Cursor context for managing transactions.
    """

    def fetchall(self) -> list[_TT]:
        """
        Return all (remaining) rows of a query result as a list.
        Return an empty list if no rows are available. Note that the arraysize attribute can
        affect the performance of this operation.
        """
        ...

    def fetchmany(self, size: int | None = ...) -> list[_TT]:
        """
        Return the next set of rows of a query result as a list. Return an empty list if no more rows are available.

        The number of rows to fetch per call is specified by the size parameter. If size is not given, arraysize
        determines the number of rows to be fetched. If fewer than size rows are available, as many rows as are
        available are returned.

        Note there are performance considerations involved with the size parameter. For optimal performance,
        it is usually best to use the arraysize attribute. If the size parameter is used,
        then it is best for it to retain the same value from one fetchmany() call to the next.
        """
        ...

    def fetchone(self) -> _TT:
        """
        If row_factory is None, return the next row query result set as a tuple. Else, pass it to the row factory
        and return its result. Return None if no more data is available.
        """
        ...

    def __iter__(self) -> typing.Self: ...
    def __next__(self) -> _TT: ...

    # New methods
    def rollback(self) -> None:
        """
        It is a shorthand for `cursor.connection.rollback()`.
        """
        ...

    def commit(self) -> None:
        """
        It is a shorthand for `cursor.connection.rollback()`.
        """
        ...

    def selectall(self, __sql: str, __parameters=()) -> typing.List[_TT]:
        """
        It is a shorthand for `cursor.execute(__sql, __parameters).fetchall()`.
        """
        ...

    def selectmany(self, __sql: str, __parameters=(), size: int = -1) -> typing.List[_TT]:
        """
        It is a shorthand for `cursor.execute(__sql, __parameters).fetchmany(size)`.
        """
        ...

    def selectone(self, __sql: str, __parameters=()) -> typing.Optional[_TT]:
        """
        It is a shorthand for `cursor.execute(__sql, __parameters).fetchone()`.
        """
        ...

class TxContext(typing.Generic[_TT]):
    """
    Transaction context for managing transactions.
    """

    _cursor: Cursor[_TT]
    _lock: _thread.LockType

    def __init__(
        self,
        connection: Connection,
        factory: typing.Optional[typing.Type[_TT]] = RowModel,
        begin: bool = False,
        autocommit: bool = False,
        isolation_level: typing.Optional[_IsolationLevel] = None,
        block: bool = False,
    ) -> None:
        """
        See `Connection.context()` for details.
        """
        ...

    def make(self) -> Cursor[_TT]:
        """
        Initializes the context (and if the begin is True, creates a transaction) and returns the cursor.

        We recommended to use `with` statement.

        Example::

            ctx = conn.context()
            cursor = ctx.make()
            # ...
            ctx.close()

            # recommnded way:
            with conn.context() as cursor:
                # ...
        """
        ...

    def close(self, rollback: bool = False) -> None:
        """
        Closes the context and cursor, (and ends the created transaction).
        """
        ...

    def __enter__(self) -> Cursor[_TT]: ...
    def __exit__(self, __exc_type, __exc_value, __traceback): ...

class Connection(sqlite3.Connection):
    """
    Each open SQLite database is represented by a `Connection` object, which is created using `sqlitehint.connect()`.
    """

    row_factory: typing.Union[typing.Any, RowModel]

    if sys.version_info >= (3, 12):
        def __init__(
            self,
            database: StrOrBytesPath,
            timeout: float = ...,
            detect_types: int = ...,
            isolation_level: typing.Optional[_IsolationLevel] = ...,
            check_same_thread: bool = ...,
            factory: typing.Optional[typing.Type[sqlite3.Connection]] = ...,
            cached_statements: int = ...,
            uri: bool = ...,
            autocommit: bool = ...,
            *,
            context_block: bool = ...,
        ) -> None:
            """
            See `sqlitehint.connect()` for details.
            """
            ...
    else:
        def __init__(
            self,
            database: StrOrBytesPath,
            timeout: float = ...,
            detect_types: int = ...,
            isolation_level: typing.Optional[_IsolationLevel] = ...,
            check_same_thread: bool = ...,
            factory: typing.Optional[typing.Type[sqlite3.Connection]] = ...,
            cached_statements: int = ...,
            uri: bool = ...,
            *,
            context_block: bool = ...,
        ) -> None:
            """
            See `sqlitehint.connect()` for details.
            """
            ...

    @property
    def is_closed(self) -> bool:
        """
        Returns True if the connection is closed.
        """
        ...

    @typing.overload
    def context(
        self,
        factory: typing.Union[
            typing.Type[_TT],
            typing.Callable[[sqlite3.Cursor, typing.Tuple[typing.Any, ...]], _TT],
        ] = RowModel,
        begin: bool = False,
        autocommit: bool = False,
        isolation_level: typing.Optional[_IsolationLevel] = None,
        *,
        block: bool = ...,
    ) -> TxContext[_TT]:
        """
        Creates a context and manage transactions.

        Parameters:
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
        """
        ...

    @typing.overload
    def context(
        self,
        factory: None = None,
        begin: bool = False,
        autocommit: bool = False,
        isolation_level: typing.Optional[_IsolationLevel] = None,
        *,
        block: bool = ...,
    ) -> TxContext[typing.Tuple]: ...
    def pragma(
        self,
        key: str,
        value: typing.Any = ...,
        cursor: typing.Optional[sqlite3.Cursor] = None,
    ) -> typing.Optional[typing.Tuple[typing.Any, ...]]:
        """
        Executes the PRAGMA statements.

        Example::

            >>> conn.pragma("journal_mode", "wal")
            >>> conn.pragma("journal_mode")
            ('wal',)
        """
        ...

    def tuning(
        self,
        vacuum: bool = ...,
        journal_mode: _JournalMode = ...,
        journal_size_limit: int = ...,
        synchronous: _Synchronous = ...,
        cursor: typing.Optional[sqlite3.Cursor] = None,
    ) -> typing.Self:
        """
        You can use it for change some connection settings and clean database to speed-up the database.

        Example::

            >>> conn = sqlitehint.connect("test.db").tuning(vacuum=True, journal_mode="WAL", synchronous="NORMAL")
            >>> conn.pragma("journal_mode")
            ('wal',)
            >>> conn.pragma("synchronous")
            (1,)
        """
        ...

    def __del__(self) -> None: ...

if sys.version_info >= (3, 12):
    @typing.overload
    def connect(
        database: StrOrBytesPath,
        timeout: float = ...,
        detect_types: int = ...,
        isolation_level: typing.Optional[_IsolationLevel] = ...,
        check_same_thread: bool = ...,
        factory: typing.Optional[typing.Type[sqlite3.Connection]] = ...,
        cached_statements: int = ...,
        uri: bool = ...,
        autocommit: bool = ...,
        *,
        context_block: bool = ...,
    ) -> Connection: ...

else:
    @typing.overload
    def connect(
        database: StrOrBytesPath,
        timeout: float = ...,
        detect_types: int = ...,
        isolation_level: typing.Optional[_IsolationLevel] = ...,
        check_same_thread: bool = ...,
        factory: typing.Optional[typing.Type[sqlite3.Connection]] = ...,
        cached_statements: int = ...,
        uri: bool = ...,
        *,
        context_block: bool = ...,
    ) -> Connection: ...

@typing.overload
def connect(*args, **kwargs) -> Connection:
    """
    Open a connection to an SQLite database.

    Parameters:
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
    """
    ...
