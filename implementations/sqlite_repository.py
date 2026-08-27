# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 12:16:07 2026

@author: Johnson
"""

# Implementation Module: 
# - Concrete sqlite3 implementation of interfaces/repository.py.

import sqlite3
from typing import List, Tuple, Optional, Dict
from typing_extensions import override
from interfaces.repository import Repository

class SqliteRepository(Repository):
    def __init__(self, db_name: str, table_name: str, columns: Tuple[str, ...]):
        self.db_name = db_name
        self.table_name = table_name
        self.columns = columns
        self.conn: Optional[sqlite3.Connection] = None
        self.cur: Optional[sqlite3.Cursor] = None

    @override
    def open(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cur = self.conn.cursor()
            self._create_table()
            return True
        except Exception as e:
            print(f"Database open fail : {e}")
            return False

    @override
    def insert(self, values: Dict[str, str]) -> bool:
        try:
            data = tuple(values[col] for col in self.columns[1:])
            placeholders: str = ', '.join('?' * len(data))
            cols: str = ', '.join(f'"{col}"' for col in self.columns[1:])
            sql: str = f'INSERT INTO "{self.table_name}" ({cols}) VALUES ({placeholders});'

            self.cur.execute(sql, data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Database insert fail : {e}")
            return False

    @override
    def select_all(self) -> List[Tuple]:
        try:
            sql: str = f'SELECT * FROM "{self.table_name}";'
            return list(self.cur.execute(sql))
        except Exception as e:
            print(f"Database select fail : {e}")
            return []

    @override
    def update(self, record_id: int, values: Dict[str, str]) -> bool:
        try:
            set_clause: str = ', '.join(f'"{col}" = ?' for col in values.keys())
            data = tuple(values.values()) + (record_id,)
            sql: str = f'UPDATE "{self.table_name}" SET {set_clause} WHERE "{self.columns[0]}" = ?;'

            self.cur.execute(sql, data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Database update fail : {e}")
            return False

    @override
    def delete(self, record_id: Optional[int] = None) -> bool:
        try:
            sql: str = f'DELETE FROM "{self.table_name}"'
            data: Tuple = ()

            if record_id is not None:
                sql += f' WHERE "{self.columns[0]}" = ?'
                data = (record_id,)

            self.cur.execute(sql + ";", data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Database delete fail : {e}")
            return False

    @override
    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.cur = None
            self.conn = None

    @override
    def is_connected(self) -> bool:
        return self.conn is not None

    def _create_table(self) -> None:
        sql: str = f"""
            CREATE TABLE IF NOT EXISTS "{self.table_name}" (
            "{self.columns[0]}" INTEGER PRIMARY KEY AUTOINCREMENT,
            "{self.columns[1]}" TEXT UNIQUE NOT NULL
        """

        for col in self.columns[2:]:
            sql += f',"{col}" TEXT'

        sql += ");"

        self.cur.execute(sql)
        self.conn.commit()