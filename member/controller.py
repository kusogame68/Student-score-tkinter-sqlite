# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 22:45:02 2026

@author: Johnson
"""

# Business Logic Module:
# - Wires AccountService, Repository, and View.

from typing import List, Tuple
from interfaces.repository import Repository
from interfaces.view import View
from member.service import AccountService
from tools.csv_exporter import export_csv

class AccountController:
    def __init__(self, repository: Repository, view: View, columns: Tuple[str, ...], csv_filename: str):
        self.repository = repository
        self.view = view
        self.columns = columns
        self.subjects = columns[1:]
        self.csv_filename = csv_filename

        self.view.bind_commands({
            '新增': self.on_add,
            '查詢': self.on_query,
            '修改': self.on_update,
            '刪除': self.on_delete,
            '開啟': self.on_open,
            '結束': self.on_close,
        })

    def on_open(self) -> None:
        if self.repository.is_connected():
            self.view.set_status('Open Already!', 'pink')
            self.view.show_warning('檔案狀態 : 開啟中!')
            return

        if self.repository.open():
            self.view.refresh_list(self.repository.select_all())
            self.view.set_status('Open data success!', 'green')
        else:
            self.view.set_status('Open data fail!', 'red')
            self.view.show_error('開啟失敗!')

    def on_add(self) -> None:
        if not self._check_open():
            return

        values = self.view.get_form_data()
        error = AccountService.validate_form(values)
        if error:
            self.view.show_error(error)
            return

        account = values[self.subjects[0]]
        if AccountService.is_duplicate(account, self.repository.select_all()):
            self.view.set_status('Add data already!', 'red')
            self.view.show_warning('資料已經寫入，請重新輸入!')
            return

        if self.repository.insert(values):
            self.view.refresh_list(self.repository.select_all())
            self.view.set_status('Add data success!', 'green')
            summary = '\n'.join(f'{key}:{val}' for key, val in values.items())
            self.view.show_info(f'{summary}\n寫入成功!')
        else:
            self.view.set_status('Add data fail!', 'red')
            self.view.show_error('輸入資料有誤!')

    def on_query(self) -> None:
        if not self._check_open():
            return

        data = self.repository.select_all()
        self.view.refresh_list(data)
        self.view.set_status(f'Have {len(data)} datas!', 'green')
        self.view.show_info(f'目前有{len(data)}筆資料!')

    def on_update(self) -> None:
        if not self._check_open():
            return

        all_data = self.repository.select_all()
        if not all_data:
            self._show_no_data()
            return

        values = self.view.get_form_data()
        account = values[self.subjects[0]]
        password = values[self.subjects[1]]
        selected = self.view.get_selected()

        if not password:
            self.view.show_warning('請輸入需要更新的資料!')
            return

        if not selected and not account:
            self.view.show_warning('請輸入需要更新的對象!')
            return

        record = selected if selected else self._find_by_account(account, all_data)
        if record is None:
            self.view.set_status('Not found file!', 'red')
            self.view.show_warning('查無此資料!')
            return

        if self.repository.update(record[0], {self.subjects[1]: password}):
            self.view.refresh_list(self.repository.select_all())
            self.view.set_status('Update data success!', 'green')
            self.view.show_info('資料已修改!')
        else:
            self.view.set_status('Update fail!', 'red')
            self.view.show_error('修改失敗!')

    def on_delete(self) -> None:
        if not self._check_open():
            return

        all_data = self.repository.select_all()
        if not all_data:
            self._show_no_data()
            return

        selected = self.view.get_selected()
        account = self.view.get_form_data()[self.subjects[0]]

        if selected:
            record_id = selected[0]
        elif account:
            record = self._find_by_account(account, all_data)
            if record is None:
                self.view.set_status('Not found file!', 'red')
                self.view.show_warning('查無此資料!')
                return
            record_id = record[0]
        else:
            if not self.view.ask_confirm('資料將會全部刪除,\n確定嗎?'):
                return
            record_id = None

        if self.repository.delete(record_id):
            self.view.refresh_list(self.repository.select_all())
            self.view.set_status('Delete data success!', 'green')
            self.view.show_info('資料已刪除!')
        else:
            self.view.set_status('Delete fail!', 'red')
            self.view.show_error('刪除失敗!')

    def on_close(self) -> None:
        if self.repository.is_connected():
            export_csv(self.columns, self.repository.select_all(), self.csv_filename)
            self.repository.close()
        self.view.close()

    def _check_open(self) -> bool:
        if not self.repository.is_connected():
            self.view.set_status('Open not yet!', 'pink')
            self.view.show_warning('請先點選「開啟」按鈕!')
            return False
        return True

    def _show_no_data(self) -> None:
        self.view.set_status('No data!', 'pink')
        self.view.show_warning('目前無資料!')

    def _find_by_account(self, account: str, all_data: List[Tuple]) -> Tuple:
        for row in all_data:
            if row[1] == account:
                return row
        return None