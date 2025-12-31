# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 23:24:14 2023

@author: Johnson
"""

import os
import sqlite3
import pandas as pd
import tkinter as tk
import tkinter.messagebox as msg
from Base import BaseManagementUI, Database
from typing import List, Tuple, Optional, Dict

"""
    Student Score Management System
    Functional Overview:
        1. Score Data Management: Maintain comprehensive student academic records.
        2. Auto-Average: Automatically calculate average scores upon data entry.
        3. CSV Export: Support data export with integrated total scores and grade levels.
        4. Authentication: Integrated login system for secure access.
"""

class StudentScoreSystem(BaseManagementUI):

    def __init__(self, iconbitmap: Optional[str] = None):
        super().__init__('學生成績建檔系統', None, iconbitmap)

        columns = ('id', '學號', '姓名', '國文', '英文', '數學', '平均分')
        self.db = Database('學生成績建檔系統.db', 'person', columns)
        self.create_status_bar(f'歡迎使用 {self.win.title()}')

        fields = [
            ('學號', False),
            ('姓名', False),
            ('國文', False),
            ('英文', False),
            ('數學', False)
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

        data = self.get_form_data()

        if any(v == '' for v in data.values()):
            self.show_error('請輸入完整資料!')
            return

        existing: List[str] = [r[1] for r in self.db.select_all()]
        if data['學號'] in existing:
            self.set_status('Add data already!', 'red')
            self.show_warning('資料已經寫入，請重新輸入!')
            return

        try:
            scores = [float(data['國文']), float(data['英文']), float(data['數學'])]
            avg    = round(sum(scores) / len(scores), 1)

        except ValueError:
            self.show_error('成績必須是數字!')
            return

        insert_data = (data['學號'], data['姓名'], data['國文'], data['英文'], data['數學'], str(avg))

        if self.db.insert(insert_data):
            self.refresh_list(self.db.select_all())
            self.set_status('Add data success!', 'green')
            summary = '\n'.join(f'{k}:{v}' for k, v in data.items())
            summary += f'\n平均分:{avg}'
            self.show_info(f'{summary}\n寫入成功!')
        else:
            self.set_status('Add data fail!', 'red')
            self.show_error('輸入資料有誤!')

    def on_query(self) -> None:

        if not self._check_db():
            return

        data = self.db.select_all()
        self.refresh_list(data)
        self.set_status(f'Have {len(data)} datas!', 'green')
        self.show_info(f'目前有{len(data)}筆資料!')

    def on_update(self) -> None:

        if not self._check_db():
            return

        all_data = self.db.select_all()
        if not all_data:
            self._show_no_data()
            return

        form_data = self.get_form_data()
        selected  = self.get_selected()

        non_id_data = {k: v for k, v in form_data.items() if k != '學號'}
        if all(v == '' for v in non_id_data.values()):
            self.show_warning('請輸入需要更新的資料!')
            return

        if not selected and not form_data['學號']:
            self.show_warning('請輸入需要更新的對象!')
            return

        update_sql = self._build_update_sql(form_data, selected, all_data)

        if not update_sql:
            self.set_status('Not found file!', 'red')
            self.show_warning('查無此資料!')
            return

        if self.db.update(update_sql):
            self.refresh_list(self.db.select_all())
            self.set_status('Update data success!', 'green')
            self.show_info('資料已修改!')
        else:
            self.set_status('Update fail!', 'red')
            self.show_error('修改失敗!')

    def on_delete(self) -> None:

        if not self._check_db():
            return

        all_data = self.db.select_all()
        if not all_data:
            self._show_no_data()
            return

        selected   = self.get_selected()
        student_id = self.get_form_data()['學號']

        condition = None

        if selected:
            condition = f"{self.db.columns[0]} = {selected[0]}"
        elif student_id:
            existing = [r[1] for r in all_data]
            if student_id not in existing:
                self.set_status('Not found file!', 'red')
                self.show_warning('查無此資料!')
                return
            condition = f"{self.db.columns[1]} = '{student_id}'"
        else:
            if not self.ask_confirm('資料將會全部刪除,\n確定嗎?'):
                return

        if self.db.delete(condition):
            self.refresh_list(self.db.select_all())
            self.set_status('Delete data success!', 'green')
            self.show_info('資料已刪除!')
        else:
            self.set_status('Delete fail!', 'red')
            self.show_error('刪除失敗!')

    def on_close(self) -> None:

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

    def _build_update_sql(self, form_data: Dict, selected: Optional[Tuple], all_data: List[Tuple]) -> Optional[str]:

        scores    = []
        sql_parts = []

        if selected:
            """
                Update from selected.
            """
            record = selected
            name   = form_data['姓名'] if form_data['姓名'] else record[2]
            sql_parts.append(f"{self.db.columns[2]} = '{name}'")

            for i, subject in enumerate(['國文', '英文', '數學'], start=3):
                score = form_data[subject] if form_data[subject] else record[i]
                sql_parts.append(f"{self.db.columns[i]} = '{score}'")
                scores.append(float(score))

            avg = round(sum(scores) / len(scores), 1)
            sql_parts.append(f"平均分 = {avg}")

            return ', '.join(sql_parts) + f" WHERE {self.db.columns[0]} = {record[0]};"
        else:
            """
                Update from student ID.
            """
            student_id = form_data['學號']
            record     = None
            for r in all_data:
                if r[1] == student_id:
                    record = r
                    break

            if not record:
                return None

            name = form_data['姓名'] if form_data['姓名'] else record[2]
            sql_parts.append(f"{self.db.columns[2]} = '{name}'")

            for i, subject in enumerate(['國文', '英文', '數學'], start = 3):
                score = form_data[subject] if form_data[subject] else record[i]
                sql_parts.append(f"{self.db.columns[i]} = '{score}'")
                scores.append(float(score))

            avg = round(sum(scores) / len(scores), 1)
            sql_parts.append(f"平均分 = {avg}")

            return ', '.join(sql_parts) + f" WHERE {self.db.columns[1]} = '{student_id}';"

    def _export_csv(self):

        data = self.db.select_all()
        if not data:
            return

        try:
            df        = pd.DataFrame(data, columns=self.db.columns)
            df['總分'] = df[['國文', '英文', '數學']].astype(int).sum(axis=1)

            def get_level(avg):
                avg = int(avg)
                if avg >= 100: 
                    return 'A'
                elif avg >= 90: 
                    return 'B'
                elif avg >= 80: 
                    return 'C'
                elif avg >= 70: 
                    return 'D'
                elif avg >= 60: 
                    return 'E'
                else: 
                    return 'F'

            df['評級'] = df['平均分'].astype(float).apply(get_level)
            df.to_csv(self.db.db_name.replace('.db', '.csv'), encoding='utf-8-sig', index=False)

        except Exception as e:
            print(f"Export CSV fail : {e}")

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

        self._create_ui()
    
    def _create_ui(self) -> None:

        font = ("標楷體", 14)
        frame = tk.Frame(self.win)
        frame.pack(expand=1, fill='both')

        tk.Label(frame, text='帳號:', font=font).pack(expand=1)
        self.entry_username = tk.Entry(frame, justify='center', font=font)
        self.entry_username.pack(expand=1)

        tk.Label(frame, text='密碼:', font=font).pack(expand=1)
        self.entry_password = tk.Entry(frame, justify='center', show='*', font=font)
        self.entry_password.pack(expand=1)

        tk.Button(frame, text='登入', font=font, command=self._on_login).pack(expand=1)

    def _on_login(self) -> None:

        username = self.entry_username.get()
        password = self.entry_password.get()

        if not os.path.exists('登入系統.db'):
            msg.showwarning('Warning', '目前無資料!')
            return

        try:
            with sqlite3.connect('登入系統.db') as conn:
                cur = conn.cursor()
                sql = "SELECT * FROM person;"
                result = cur.execute(sql)

                if any(r[1] == username and r[2] == password for r in result):
                    msg.showinfo('Success', '登入成功!')
                    self.win.destroy()

                    StudentScoreSystem(iconbitmap=r'..\Image\person.ico').run()
                else:
                    msg.showerror('Fail', '登入失敗!')
        except Exception as e:
            print(f"Login fail : {e}")
            msg.showerror('Fail', '登入失敗!')

    def run(self):
        self.win.mainloop()

if __name__ == '__main__':
    LoginView(iconbitmap=r'..\Image\login.ico').run()