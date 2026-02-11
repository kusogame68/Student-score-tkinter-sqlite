# -*- coding: utf-8 -*-
"""
Created on Thu Jan  1 00:02:15 2026

@author: Johnson
"""

import sqlite3
import tkinter as tk
import tkinter.messagebox as msg
from typing import List, Tuple, Optional, Dict, Callable

# Base Module:
# - Database: General-purpose database operations.
# - BaseManagementUI: Standard UI framework for management systems. 
#     Compatible with various systems like Student Scoring or Account Management.

class Database:
    def __init__(self, db_name: str, table_name: str, columns: Tuple[str, ...]):
        self.db_name = db_name
        self.table_name = table_name
        self.columns = columns
        self.conn: Optional[sqlite3.Connection] = None
        self.cur: Optional[sqlite3.Cursor] = None

    def open(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cur = self.conn.cursor()
            self._create_table()
            return True
        except Exception as e:
            print(f"Database open fail : {e}")
            return False

    def _create_table(self) -> None:
        sql : str = f"""
            CREATE TABLE IF NOT EXISTS '{self.table_name}' (
            '{self.columns[0]}' INTEGER PRIMARY KEY AUTOINCREMENT,
            '{self.columns[1]}' TEXT UNIQUE NOT NULL
        """

        for col in self.columns[2:]:
            sql += f",'{col}' TEXT"

        sql += ");"

        self.cur.execute(sql)
        self.conn.commit()

    def insert(self, data: Tuple) -> bool:
        try:
            placeholders : str = ', '.join('?' * len(data))
            cols : str = ', '.join(f"'{col}'" for col in self.columns[1:])
            sql : str = f"INSERT INTO {self.table_name} ({cols}) VALUES ({placeholders});"

            self.conn.execute(sql, data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Database insert fail : {e}")
            return False

    def select_all(self) -> List[Tuple]:
        try:
            sql : str = f"SELECT * FROM {self.table_name};"
            return list(self.cur.execute(sql))
        except Exception as e:
            print(f"Database select fail : {e}")
            return []

    def update(self, update_sql: str, data: Tuple) -> bool:
        try:
            sql : str = f"UPDATE {self.table_name} SET {update_sql}"
            self.cur.execute(sql, data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Database update fail : {e}")
            return False

    def delete(self, data: Tuple, condition: Optional[str]) -> bool:
        try:
            sql : str = f"DELETE FROM {self.table_name}"
            if condition:
                sql += f" WHERE {condition}"
            self.cur.execute(sql + ";", data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Database delete fail : {e}")
            return False

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cur = None

    def is_connected(self) -> bool:
        return self.conn is not None

class BaseManagementUI:
    def __init__(self, title: str, geometry: Optional[str] = None, iconbitmap: Optional[str] = None):
        self.win = tk.Tk()
        self.win.title(title)
        self.win.geometry(geometry)
        self.win.resizable(False, False)
        if iconbitmap:
            try:
                self.win.iconbitmap(iconbitmap)
            except Exception:
                pass

        self.status_label: Optional[tk.Label] = None
        self.entries: Dict[str, tk.Entry] = {}
        self.listbox: Optional[tk.Listbox] = None
        self.list_var = tk.StringVar()

    def create_status_bar(self, welcome_text: str) -> None:
        frame = tk.Frame(self.win, bg = 'black')
        frame.pack(fill = 'x')

        self.status_label = tk.Label(frame, text = welcome_text, bg = 'black', fg = 'white', anchor = 'w')
        self.status_label.pack(expand = 1, fill = 'x')

    def create_form(self, fields: Tuple[Tuple[str, bool]]) -> tk.Frame:
        frame = tk.Frame(self.win)
        frame.pack(fill='x')

        font_title = ("標楷體", 24)
        font_field = ("標楷體", 14)

        tk.Label(
            frame, text = self.win.title(), font = font_title
        ).grid(
            row = 0, column = 0, columnspan = 2, padx = 10, pady = 5
        )

        for _, (field_name, is_password) in enumerate(fields, start = 1):
            tk.Label(
                frame, text = field_name, font = font_field
            ).grid(
                row = _, column = 0, padx = 5, pady = 2
            )

            entry = tk.Entry(
                frame, bg = "lightyellow", fg = "black", font = font_field, borderwidth = 3, show = '*' 
                if is_password else ''
            )
            entry.grid(row = _, column = 1, pady = 10)
            self.entries[field_name] = entry
        return frame

    def create_buttons(self, commands: Dict[str, Callable]) -> tk.Frame:
        frame = tk.Frame(self.win, bg = '#d2b48c')
        frame.pack(fill = 'x')

        font = ("標楷體", 16)
        button_names = ('新增', '查詢', '修改', '刪除', '開啟', '結束')

        for _, name in enumerate(button_names[:4]):
            if name in commands:
                tk.Button(
                    frame, text = name, font = font, command = commands[name]
                ).grid(
                    row = 0, column = _, padx = 5, pady = 5, sticky = 'nswe'
                )

        tk.Button(
            frame, text = button_names[-2], font = font, command = commands['開啟']
        ).grid(
            row = 1, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = 'nswe'
        )

        tk.Button(
                frame, text = '結束', font = font, command = commands['結束']
        ).grid(
            row = 1, column = 2, columnspan = 2, padx = 5, pady = 5, sticky = 'nswe'
        )
        return frame

    def create_listbox(self) -> tk.Frame:
        frame = tk.Frame(self.win, bg = 'white')
        frame.pack(fill = 'both', expand = 1)

        self.listbox = tk.Listbox(frame, listvariable = self.list_var)
        self.listbox.pack(fill = 'both', expand = 1)
        return frame

    def set_status(self, text: str, color: str = 'green') -> None:
        if self.status_label:
            self.status_label.config(text = text, fg = color)

    def get_form_data(self) -> Dict[str, str]:
        return {name: entry.get() for name, entry in self.entries.items()}

    def refresh_list(self, data: List[Tuple]) -> None:
        self.list_var.set(data)

    def get_selected(self) -> Optional[Tuple]:
        selection = self.listbox.curselection()
        return self.listbox.get(selection[0]) if selection else None

    def show_info(self, message: str) -> None:
        msg.showinfo('Information', message)

    def show_warning(self, message: str) -> None:
        msg.showwarning('Warning', message)

    def show_error(self, message: str) -> None:
        msg.showerror('Error', message)

    def ask_confirm(self, message: str) -> bool:
        return msg.askquestion('Question', message) == 'yes'

    def run(self) -> None:
        self.win.mainloop()