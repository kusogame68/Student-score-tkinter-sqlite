# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 22:45:02 2026

@author: Johnson
"""

# Business Logic Module:
# - Account validation rules.

from typing import Dict, List, Tuple, Optional

class AccountService:
    @staticmethod
    def validate_form(values: Dict[str, str]) -> Optional[str]:
        if any(val == '' for val in values.values()):
            return '請輸入完整資料!'
        return None

    @staticmethod
    def is_duplicate(account: str, existing_accounts: List[Tuple]) -> bool:
        return any(row[1] == account for row in existing_accounts)