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

# Student Score Management System
# Functional Overview:
#     1. Score Data Management: Maintain comprehensive student academic records.
#     2. Auto-Average: Automatically calculate average scores upon data entry.
#     3. CSV Export: Support data export with integrated total scores and grade levels.
#     4. Authentication: Integrated login system for secure access.

class StudentApp(BaseManagementUI):
    def __init__(self, iconbitmap: Optional[str] = None):
        super().__init__('學生成績建檔系統', None, iconbitmap)

        self.columns = ('id', '學號', '姓名', '國文', '英文', '數學', '平均分')
        self.db = Database('學生成績建檔系統.db', 'person', self.columns)
        self.create_status_bar(f'歡迎使用 {self.win.title()}')

        fields = ((col, False) for col in self.columns[1:-1])
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

        existing: List[str] = [row[1] for row in self.db.select_all()]
        if datas['學號'] in existing:
            self.set_status('Add data already!', 'red')
            self.show_warning('資料已經寫入，請重新輸入!')
            return

        try:
            scores = self._validate_scores(datas)
            avg = round(sum(scores) / len(scores), 1)
        except ValueError as e:
            self.show_error(str(e))
            return

        insert_data = tuple([datas[col] for col in self.columns[1:-1]] + [str(avg)])

        if self.db.insert(insert_data):
            self.refresh_list(self.db.select_all())
            self.set_status('Add data success!', 'green')
            summary = '\n'.join(f'{key}:{val}' for key, val in datas.items())
            summary += f'\n{self.columns[-1]}:{avg}'
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

        form_data = self.get_form_data()
        selected = self.get_selected()

        non_id_data = {key: val for key, val in form_data.items() if key != self.columns[1]}
        if all(val == '' for val in non_id_data.values()):
            self.show_warning('請輸入需要更新的資料!')
            return

        if not selected and not form_data[self.columns[1]]:
            self.show_warning('請輸入需要更新的對象!')
            return

        try:
            for subject in self.columns[3:-1]:
                if form_data[subject]:
                    score = float(form_data[subject])
                    if not 0 <= score <= 100:
                        raise ValueError(f"{subject}分數必須在 0-100 之間 (輸入: {score})")
        except ValueError as e:
            self.show_error(str(e))
            return

        update_sql = self._build_update_sql(form_data, selected, all_datas)

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

        all_datas = self.db.select_all()
        if not all_datas:
            self._show_no_data()
            return

        selected = self.get_selected()
        student_id = self.get_form_data()[self.columns[1]]

        condition = None

        if selected:
            condition = f"{self.db.columns[0]} = {selected[0]}"
        elif student_id:
            existing = [data[1] for data in all_datas]
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

    def _validate_scores(self, datas: Dict) -> List[float]:
        scores = []
        for subject in self.columns[3:-1]:
            score_str = datas[subject]
            try:
                score = float(score_str)
            except ValueError:
                raise ValueError(f"{subject}必須是數字! (輸入: {score_str})")

            if not 0 <= score <= 100:
                raise ValueError(f"{subject}分數必須在 0-100 之間 (輸入: {score})")

            scores.append(score)
        return scores

    def _show_no_data(self):
        self.set_status('No data!', 'pink')
        self.show_warning('目前無資料!')

    def _build_update_sql(self, form_data: Dict, selected: Optional[Tuple], all_datas: List[Tuple]) -> Optional[str]:
        if selected:
            record = selected
        else:
            student_id = form_data[self.columns[1]]
            record = self._find_record_by_id(student_id, all_datas)
            if not record:
                return None

        name = form_data['姓名'] if form_data['姓名'] else record[2]
        sql_parts = [f"{self.db.columns[2]} = '{name}'"]

        scores = []
        for i, subject in enumerate(self.columns[3:-1], start = 3):
            score = form_data[subject] if form_data[subject] else record[i]
            sql_parts.append(f"{self.db.columns[i]} = '{score}'")
            scores.append(float(score))

        avg = round(sum(scores) / len(scores), 1)
        sql_parts.append(f"平均分 = {avg}")

        where_clause = f"WHERE {self.db.columns[0]} = {record[0]}" if selected else f"WHERE {self.db.columns[1]} = '{form_data['學號']}'"

        return ', '.join(sql_parts) + f" {where_clause};"

    def _find_record_by_id(self, student_id: str, all_datas: List[Tuple]) -> Optional[Tuple]:
        for data in all_datas:
            if data[1] == student_id:
                return data
        return None

    def _export_csv(self):
        datas = self.db.select_all()
        if not datas:
            return

        try:
            df = pd.DataFrame(datas, columns = self.db.columns)
            df['總分'] = df[list(self.columns[3:-1])].astype(int).sum(axis=1)

            def get_level(avg: float) -> str:
                thresholds = ((100, 'A'), (90, 'B'), (80, 'C'), (70, 'D'), (60, 'E'))
                return next((grade for threshold, grade in thresholds if avg >= threshold), 'F')

            df['評級'] = df['平均分'].astype(float).apply(get_level)
            df.to_csv(self.db.db_name.replace('.db', '.csv'), encoding = 'utf-8-sig', index = False)
        except Exception:
            self.show_error("匯出CSV失敗!")

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
        frame.pack(expand = 1, fill = 'both')

        tk.Label(frame, text = '帳號:', font = font).pack(expand = 1)
        self.entry_username = tk.Entry(frame, justify = 'center', font = font)
        self.entry_username.pack(expand=1)

        tk.Label(frame, text = '密碼:', font = font).pack(expand = 1)
        self.entry_password = tk.Entry(frame, justify = 'center', show='*', font = font)
        self.entry_password.pack(expand = 1)

        tk.Button(frame, text = '登入', font = font, command = self._on_login).pack(expand = 1)

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
                results = cur.execute(sql)

                if any(result[1] == username and result[2] == password for result in results):
                    msg.showinfo('Success', '登入成功!')
                    self.win.destroy()

                    StudentApp(iconbitmap = r'..\Image\person.ico').run()
                else:
                    msg.showerror('Fail', '登入失敗!')
        except Exception:
            msg.showerror('Fail', '登入失敗!')

    def run(self):
        self.win.mainloop()

if __name__ == '__main__':
    LoginView(iconbitmap = r'..\Image\login.ico').run()