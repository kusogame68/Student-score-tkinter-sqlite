# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 11:29:19 2026

@author: Johnson
"""

# Business Logic Module:
# - Connects LoginView to a Repository.
# - Doesn't know about gradebook — success calls on_success, given by main.py.

from typing import Callable
from interfaces.repository import Repository
from login.view import LoginView

class LoginController:
    def __init__(self, repository: Repository, view: LoginView, on_success: Callable[[], None]):
        self.repository = repository
        self.view = view
        self.on_success = on_success
        self.view.bind_login(self.handle_login)

    def handle_login(self, account: str, password: str) -> None:
        if not self.repository.open():
            self.view.show_error('登入失敗!')
            return

        accounts = self.repository.select_all()
        self.repository.close()

        matched = any(row[1] == account and row[2] == password for row in accounts)

        if matched:
            self.view.close()
            self.on_success()
        else:
            self.view.show_error('登入失敗!')