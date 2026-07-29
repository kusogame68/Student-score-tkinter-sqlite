# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 14:45:58 2026

@author: Johnson
"""

# Implementation Module:
# - Gradebook-specific screen config, built on TkManagementView.

from typing import Optional
from implementations.tk_management_view import TkManagementView

class GradebookView(TkManagementView):
    def __init__(self, iconbitmap: Optional[str] = None):
        super().__init__('學生成績建檔系統', None, iconbitmap)

        self.create_status_bar(f'歡迎使用 {self.win.title()}')
        self.create_form((
            ('學號', False),
            ('姓名', False),
            ('國文', False),
            ('英文', False),
            ('數學', False),
        ))
        self.create_buttons(('新增', '查詢', '修改', '刪除', '開啟', '結束'))
        self.create_listbox()