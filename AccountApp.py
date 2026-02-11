# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 07:27:37 2023

@author: Johnson
"""

import pandas as pd
from Base import BaseManagementUI, Database
from typing import Optional

# Account Management System
# Functional Overview:
#     1. Account Creation: Create new login accounts for the system.
#     2. User Credential Management: Maintain and manage user IDs and encrypted passwords.
#     3. Account Data Export: Export complete account lists to external data files (CSV).

class AccountApp(BaseManagementUI):
    def __init__(self, iconbitmap: Optional[str] = None):
        super().__init__('登入系統', None, iconbitmap)

        columns = ('id', '帳號', '密碼')
        self.subjects = (columns[1:])
        self.db = Database('登入系統.db', 'person', columns)
        self.create_status_bar(f'歡迎使用 {self.win.title()}')

        fields = [
            (self.subjects[0], False),
            (self.subjects[1], True)
        ]
        self.create_form(fields)

        commands = {
            '新增': self.on_add,
            '查詢': self.on_query,
            '修改': self.on_update,
            '刪除': self.on_delete,
            '開啟': self.on_open,
            '結束': self.on_close
        }
        self.create_buttons(commands)
        self.create_listbox()
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_open(self) -> None:
        if self.db.is_connected():
            self.set_status('Open Already!', 'pink')
            self.show_warning('檔案狀態 : 開啟中!')
            return

        if self.db.open():
            self.refresh_list(self.db.select_all())
            self.set_status('Open data success!', 'green')
        else:
            self.set_status('Open data fail!', 'red')
            self.show_error('開啟失敗!')

    def on_add(self) -> None:
        if not self._check_db():
            return

        datas = self.get_form_data()
        if any(val == '' for val in datas.values()):
            self.show_error('請輸入完整資料!')
            return

        existing = [row[1] for row in self.db.select_all()]
        if datas[self.subjects[0]] in existing:
            self.set_status('Add data already!', 'red')
            self.show_warning('資料已經寫入，請重新輸入!')
            return

        insert_data = (datas[self.subjects[0]], datas[self.subjects[1]])

        if self.db.insert(insert_data):
            self.refresh_list(self.db.select_all())
            self.set_status('Add data success!', 'green')
            summary = '\n'.join(f'{key}:{val}' for key, val in datas.items())
            self.show_info(f'{summary}\n寫入成功!')
        else:
            self.set_status('Add data fail!', 'red')
            self.show_error('輸入資料有誤!')

    def on_query(self) -> None:
        if not self._check_db():
            return

        datas = self.db.select_all()
        self.refresh_list(datas)
        self.set_status(f'Have {len(datas)} datas!', 'green')
        self.show_info(f'目前有{len(datas)}筆資料!')

    def on_update(self) -> None:
        if not self._check_db():
            return

        all_datas = self.db.select_all()
        if not all_datas:
            self._show_no_data()
            return

        account = self.get_form_data()[self.subjects[0]]
        password = self.get_form_data()[self.subjects[1]]
        selected = self.get_selected()

        if not password:
            self.show_warning('請輸入需要更新的資料!')
            return

        if not selected and not account:
            self.show_warning('請輸入需要更新的對象!')
            return

        if selected:
            update_sql = f"{self.db.columns[2]} = ? WHERE {self.db.columns[0]} = ?"
            data = (password, selected[0])
        else:
            existing = [data[1] for data in all_datas]
            if account not in existing:
                self.set_status('Not found file!', 'red')
                self.show_warning('查無此資料!')
                return
            update_sql = f"{self.db.columns[2]} = ? WHERE {self.db.columns[1]} = ?"
            data = (password, account)

        if self.db.update(update_sql, data):
            self.refresh_list(self.db.select_all())
            self.set_status('Update data success!', 'green')
            self.show_info('資料已修改!')
        else:
            self.set_status('Update fail!', 'red')
            self.show_error('修改失敗!')

    def on_delete(self) -> None:
        if not self._check_db():
            return

        all_datas = self.db.select_all()
        if not all_datas:
            self._show_no_data()
            return

        selected = self.get_selected()
        account = self.get_form_data()[self.subjects[0]]

        if selected:
            condition = f"{self.db.columns[0]} = ?"
            data = (selected[0],)
        elif account:
            existing = [data[1] for data in all_datas]
            if account not in existing:
                self.set_status('Not found file!', 'red')
                self.show_warning('查無此資料!')
                return
            condition = f"{self.db.columns[1]} = ?"
            data = (account,)
        else:
            if not self.ask_confirm('資料將會全部刪除,\n確定嗎?'):
                return
            condition = None
            data = ()

        if self.db.delete(data, condition):
            self.refresh_list(self.db.select_all())
            self.set_status('Delete data success!', 'green')
            self.show_info('資料已刪除!')
        else:
            self.set_status('Delete fail!', 'red')
            self.show_error('刪除失敗!')

    def on_close(self) -> None:
        if self.db.is_connected():
            self._export_csv()
            self.db.close()
        self.win.destroy()

    def _check_db(self) -> bool:
        if not self.db.is_connected():
            self.set_status('Open not yet!', 'pink')
            self.show_warning('請先點選「開啟」按鈕!')
            return False
        return True

    def _show_no_data(self):
        self.set_status('No data!', 'pink')
        self.show_warning('目前無資料!')

    def _export_csv(self):
        datas = self.db.select_all()
        if not datas:
            return

        try:
            df = pd.DataFrame(datas, columns = self.db.columns)
            df.to_csv(self.db.db_name.replace('.db', '.csv'), encoding = 'utf-8-sig', index = False)

        except Exception as e:
            print(f"Export CSV fail : {e}")

if __name__ == '__main__':
    AccountApp(iconbitmap = r'..\Image\login.ico').run()