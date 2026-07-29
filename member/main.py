# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 22:45:02 2026

@author: Johnson
"""

# Composition Root:
# - Assembles the account management application.

from implementations.sqlite_repository import SqliteRepository
from member.view import AccountView
from member.controller import AccountController

def main() -> None:
    columns = ('id', '帳號', '密碼')
    repository = SqliteRepository('登入系統.db', 'person', columns)
    view = AccountView(iconbitmap = 'Image/manager.ico')

    AccountController(
        repository = repository,
        view = view,
        columns = columns,
        csv_filename = '登入系統.csv',
    )

    view.run()

if __name__ == '__main__':
    main()