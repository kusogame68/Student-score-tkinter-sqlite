# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 14:45:58 2026

@author: Johnson
"""

# Business Logic Module:
# - Wires GradebookService, Repository, and View.

from typing import List, Tuple
from interfaces.repository import Repository
from interfaces.view import View
from gradebook.service import GradebookService
from tools.csv_exporter import export_csv

class GradebookController:
    def __init__(self, repository: Repository, view: View, columns: Tuple[str, ...], csv_filename: str):
        self.repository = repository
        self.view = view
        self.columns = columns
        self.subjects = columns[3:-1]
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
        error = GradebookService.validate_form(values)
        if error:
            self.view.show_error(error)
            return

        student_id = values[self.columns[1]]
        if GradebookService.is_duplicate(student_id, self.repository.select_all()):
            self.view.set_status('Add data already!', 'red')
            self.view.show_warning('資料已經寫入，請重新輸入!')
            return

        error, scores = GradebookService.validate_scores(values, self.subjects)
        if error:
            self.view.show_error(error)
            return

        avg = GradebookService.compute_average(scores)
        insert_values = dict(values)
        insert_values[self.columns[-1]] = str(avg)

        if self.repository.insert(insert_values):
            self.view.refresh_list(self.repository.select_all())
            self.view.set_status('Add data success!', 'green')
            summary = '\n'.join(f'{key}:{val}' for key, val in values.items())
            summary += f'\n{self.columns[-1]}:{avg}'
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
        selected = self.view.get_selected()

        non_id_values = {k: v for k, v in values.items() if k != self.columns[1]}
        if all(v == '' for v in non_id_values.values()):
            self.view.show_warning('請輸入需要更新的資料!')
            return

        student_id = values[self.columns[1]]
        if not selected and not student_id:
            self.view.show_warning('請輸入需要更新的對象!')
            return

        error = GradebookService.validate_optional_scores(values, self.subjects)
        if error:
            self.view.show_error(error)
            return

        record = selected if selected else self._find_by_id(student_id, all_data)
        if record is None:
            self.view.set_status('Not found file!', 'red')
            self.view.show_warning('查無此資料!')
            return

        update_values = {self.columns[2]: values[self.columns[2]] or record[2]}
        scores = []
        for i, subject in enumerate(self.subjects, start = 3):
            score = values[subject] or record[i]
            update_values[subject] = score
            scores.append(float(score))

        avg = GradebookService.compute_average(scores)
        update_values[self.columns[-1]] = str(avg)

        if self.repository.update(record[0], update_values):
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
        student_id = self.view.get_form_data()[self.columns[1]]

        if selected:
            record_id = selected[0]
        elif student_id:
            record = self._find_by_id(student_id, all_data)
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
            self._export_csv()
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

    def _find_by_id(self, student_id: str, all_data: List[Tuple]) -> Tuple:
        for row in all_data:
            if row[1] == student_id:
                return row
        return None

    def _export_csv(self) -> None:
        data = self.repository.select_all()
        if not data:
            return

        final_columns = self.columns + ('總分', '評級')
        final_data = []
        for row in data:
            scores = [int(row[i]) for i in range(3, 3 + len(self.subjects))]
            total = sum(scores)
            grade = GradebookService.get_grade_level(float(row[-1]))
            final_data.append(row + (total, grade))

        export_csv(final_columns, final_data, self.csv_filename)