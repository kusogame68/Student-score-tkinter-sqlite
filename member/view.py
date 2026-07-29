# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 22:45:02 2026

@author: Johnson
"""

# Implementation Module:
# - Account-specific screen config, built on TkManagementView.

from typing import Optional
from implementations.tk_management_view import TkManagementView

class AccountView(TkManagementView):
    def __init__(self, iconbitmap: Optional[str] = None):
        super().__init__('登入系統', None, iconbitmap)

        self.create_status_bar(f'歡迎使用 {self.win.title()}')
        self.create_form((('帳號', False), ('密碼', True)))
        self.create_buttons(('新增', '查詢', '修改', '刪除', '開啟', '結束'))
        self.create_listbox()
