# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 12:16:07 2026

@author: Johnson
"""

# Implementation Module: 
# - Concrete tkinter implementation of interfaces/view.py.
# - Construction methods (create_form, create_buttons, etc.) are implementation
#   details used by subclasses to build their own screen.

import tkinter as tk
import tkinter.messagebox as msg
from typing import List, Tuple, Optional, Dict, Callable
from typing_extensions import override
from interfaces.view import View

class TkManagementView(View):
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
        self.win.protocol("WM_DELETE_WINDOW", lambda: self._dispatch('結束'))

    # --- View contract methods ---

    @override
    def bind_commands(self, commands: Dict[str, Callable]) -> None:
        self._callbacks = commands

    @override
    def get_form_data(self) -> Dict[str, str]:
        return {name: entry.get() for name, entry in self.entries.items()}

    @override
    def get_selected(self) -> Optional[Tuple]:
        selection = self.listbox.curselection()
        return self.listbox.get(selection[0]) if selection else None

    @override
    def refresh_list(self, data: List[Tuple]) -> None:
        self.list_var.set(data)

    @override
    def set_status(self, text: str, color: str = 'green') -> None:
        if self.status_label:
            self.status_label.config(text = text, fg = color)

    @override
    def show_info(self, message: str) -> None:
        msg.showinfo('Information', message)

    @override
    def show_warning(self, message: str) -> None:
        msg.showwarning('Warning', message)

    @override
    def show_error(self, message: str) -> None:
        msg.showerror('Error', message)

    @override
    def ask_confirm(self, message: str) -> bool:
        return msg.askquestion('Question', message) == 'yes'

    @override
    def close(self) -> None:
        self.win.destroy()

    # --- construction methods (not part of the View contract) ---

    def create_status_bar(self, welcome_text: str) -> None:
        frame = tk.Frame(self.win, bg = 'black')
        frame.pack(fill = 'x')

        self.status_label = tk.Label(frame, text = welcome_text, bg = 'black', fg = 'white', anchor = 'w')
        self.status_label.pack(expand = 1, fill = 'x')

    def create_form(self, fields: Tuple[Tuple[str, bool], ...]) -> tk.Frame:
        frame = tk.Frame(self.win)
        frame.pack(fill = 'x')

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

    def create_buttons(self, button_names: Tuple[str, ...]) -> tk.Frame:
        frame = tk.Frame(self.win, bg = '#d2b48c')
        frame.pack(fill = 'x')

        font = ("標楷體", 16)

        for _, name in enumerate(button_names[:4]):
            tk.Button(
                frame, text = name, font = font, command = lambda n = name: self._dispatch(n)
            ).grid(
                row = 0, column = _, padx = 5, pady = 5, sticky = 'nswe'
            )

        tk.Button(
            frame, text = button_names[-2], font = font, command = lambda: self._dispatch(button_names[-2])
        ).grid(
            row = 1, column = 0, columnspan = 2, padx = 5, pady = 5, sticky = 'nswe'
        )

        tk.Button(
            frame, text = button_names[-1], font = font, command = lambda: self._dispatch(button_names[-1])
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

    def run(self) -> None:
        self.win.mainloop()

    def _dispatch(self, action: str) -> None:
        callback = self._callbacks.get(action)
        if callback is not None:
            callback()