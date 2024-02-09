import sqlite3.dbapi2 as _dbapi_core
import typing
import _thread


class RowModel(_dbapi_core.Row):
    __slots__: tuple

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if (getattr(cls, "__slots__", None) is None) and (hasattr(cls, "__annotations__")):
            cls.__slots__ = tuple(cls.__annotations__.keys())

    def __getattr__(self, __name: str) -> typing.Any:
        return super().__getitem__(__name)

    def __repr__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={!r}".format(k, getattr(self, k, None)) for k in self.keys()),
        )


_TT = typing.TypeVar("_TT")


class Cursor(_dbapi_core.Cursor, typing.Generic[_TT]):
    def rollback(self) -> None:
        self.connection.rollback()

    def commit(self) -> None:
        self.connection.commit()

    def selectall(self, __sql: str, __parameters=()) -> typing.List[_TT]:
        return self.execute(__sql, __parameters).fetchall()

    def selectmany(self, __sql: str, __parameters=(), size: int = -1) -> typing.List[_TT]:
        return self.execute(__sql, __parameters).fetchmany(size=size)

    def selectone(self, __sql: str, __parameters=()) -> typing.Optional[_TT]:
        return self.execute(__sql, __parameters).fetchone()


class TxContext(typing.Generic[_TT]):
    def __init__(
        self,
        connection: "Connection",
        factory: typing.Optional[typing.Type[_TT]] = RowModel,
        begin: bool = False,
        autocommit: bool = False,
        isolation_level: typing.Optional[str] = None,
        block: bool = False,
    ) -> None:
        self._cursor = Cursor(connection)
        self._cursor.row_factory = factory

        self._lock = connection._lock if block else None
        self._options = (begin, isolation_level or "")
        self._autocommit = autocommit

    def _initialize(self) -> None:
        self._cursor.execute(("BEGIN %s" % self._options[1]).strip())

    def _rollback(self) -> None:
        self._cursor.connection.rollback()

    def _commit(self) -> None:
        self._cursor.connection.commit()

    def make(self) -> Cursor[_TT]:
        if self._lock is not None:
            self._lock.acquire()

        if self._options[0]:
            self._initialize()

        return self._cursor

    def close(self, rollback: bool = False) -> None:
        try:
            if self._options[0] or self._autocommit:
                (self._commit, self._rollback)[rollback]()

        finally:
            if self._lock is not None:
                self._lock.release()

        try:
            self._cursor.close()
        except _dbapi_core.ProgrammingError:
            pass

    def __enter__(self) -> Cursor[_TT]:
        return self.make()

    def __exit__(self, __exc_type, *args):
        return self.close(rollback=__exc_type is not None)


class Connection(_dbapi_core.Connection):
    def __init__(self, *args, **kwds) -> None:
        self.context_block = kwds.pop("context_block", False)
        super().__init__(*args, **kwds)
        self._lock = _thread.allocate_lock()
        self._is_closed = False

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    def context(
        self,
        factory: typing.Optional[typing.Type[_TT]] = RowModel,
        begin: bool = False,
        autocommit: bool = False,
        isolation_level: typing.Optional[str] = None,
        **kwargs,
    ) -> TxContext[_TT]:
        return TxContext(
            self,
            factory,
            begin,
            autocommit,
            isolation_level or self.isolation_level,
            kwargs.get("block", self.context_block),
        )

    def pragma(
        self,
        key: str,
        value: typing.Any = None,
        cursor: typing.Optional[_dbapi_core.Cursor] = None,
    ):
        __sql = f"PRAGMA {key}"

        if value is not None:
            __sql = __sql + "=" + repr(value)

        __sql += ";"

        if cursor:
            cursor.execute(__sql)
            if value is None:
                return cursor.fetchone()

        else:
            with self.context(factory=None, block=True) as cursor:
                cursor.execute(__sql)
                if value is None:
                    return cursor.fetchone()

    def _tuning(self, cursor: _dbapi_core.Cursor, **kwargs):
        if kwargs.pop("vacuum", False):
            cursor.execute("VACUUM;")

        for key, value in filter(lambda x: bool(x[1]), kwargs.items()):
            self.pragma(key, value, cursor)

        return self

    def tuning(
        self,
        vacuum: bool = False,
        journal_mode: str = "",
        journal_size_limit: int = 0,
        synchronous: str = "",
        cursor: typing.Optional[_dbapi_core.Cursor] = None,
    ):
        if not any([vacuum, journal_mode, journal_size_limit, synchronous]):
            return

        if cursor:
            return self._tuning(
                cursor,
                vacuum=vacuum,
                journal_mode=journal_mode,
                journal_size_limit=journal_size_limit,
                synchronous=synchronous,
            )

        with self.context(block=True) as cursor:
            return self._tuning(
                cursor,
                vacuum=vacuum,
                journal_mode=journal_mode,
                journal_size_limit=journal_size_limit,
                synchronous=synchronous,
            )

    def close(self) -> None:
        super().close()
        self._is_closed = True

    def __del__(self) -> None:
        if self._is_closed:
            return

        self.close()


def connect(*args, **kwds):
    return Connection(*args, **kwds)
