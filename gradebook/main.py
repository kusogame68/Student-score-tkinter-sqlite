# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 14:45:58 2026

@author: Johnson
"""

# Composition Root: 
# - Assembles the gradebook application, gated by login.

from implementations.sqlite_repository import SqliteRepository
from login.view import LoginView
from login.controller import LoginController
from gradebook.view import GradebookView
from gradebook.controller import GradebookController

ACCOUNT_COLUMNS = ('id', '帳號', '密碼')
GRADEBOOK_COLUMNS = ('id', '學號', '姓名', '國文', '英文', '數學', '平均分')

def launch_gradebook() -> None:
    repository = SqliteRepository('學生成績建檔系統.db', 'person', GRADEBOOK_COLUMNS)
    view = GradebookView(iconbitmap = 'Image/doc.ico')

    GradebookController(
        repository = repository,
        view = view,
        columns = GRADEBOOK_COLUMNS,
        csv_filename = '學生成績建檔系統.csv',
    )

    view.run()

def main() -> None:
    account_repository = SqliteRepository('登入系統.db', 'person', ACCOUNT_COLUMNS)
    login_view = LoginView(iconbitmap = 'Image/person.ico')

    LoginController(
        repository = account_repository,
        view = login_view,
        on_success = launch_gradebook,
    )

    login_view.run()

if __name__ == '__main__':
    main()