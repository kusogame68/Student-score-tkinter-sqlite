# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:29:19 2026

@author: Johnson
"""

# Implementation Module: 
# - Login screen. Doesn't implement interfaces/view.py
# - Because its shape differs (no listbox, no CRUD buttons) — 
#   this is its own UI concern, not a ManagementView.

import tkinter as tk
import tkinter.messagebox as msg
from typing import Callable, Optional

class LoginView:
    def __init__(self, iconbitmap: Optional[str] = None):
        self.win = tk.Tk()
        self.win.title('Login')
        self.win.geometry('300x200')
        self.win.resizable(False, False)
        if iconbitmap:
            try:
                self.win.iconbitmap(iconbitmap)
            except Exception:
                pass

        self._on_login_callback: Optional[Callable[[str, str], None]] = None
        self._create_ui()

    def _create_ui(self) -> None:
        font = ("標楷體", 14)
        frame = tk.Frame(self.win)
        frame.pack(expand = 1, fill = 'both')

        tk.Label(frame, text = '帳號:', font = font).pack(expand = 1)
        self.entry_username = tk.Entry(frame, justify = 'center', font = font)
        self.entry_username.pack(expand = 1)

        tk.Label(frame, text = '密碼:', font = font).pack(expand = 1)
        self.entry_password = tk.Entry(frame, justify = 'center', show = '*', font = font)
        self.entry_password.pack(expand = 1)

        tk.Button(frame, text = '登入', font = font, command = self._handle_click).pack(expand = 1)

    def bind_login(self, callback: Callable[[str, str], None]) -> None:
        self._on_login_callback = callback

    def _handle_click(self) -> None:
        if self._on_login_callback:
            self._on_login_callback(self.entry_username.get(), self.entry_password.get())

    def show_error(self, message: str) -> None:
        msg.showerror('Fail', message)

    def close(self) -> None:
        self.win.destroy()

    def run(self) -> None:
        self.win.mainloop()