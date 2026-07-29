# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:59:32 2026

@author: Johnson
"""

# Utility Module: 
# - Export tabular data to a CSV file.

import pandas as pd
from typing import List, Tuple

def export_csv(columns: Tuple[str, ...], data: List[Tuple], filename: str) -> bool:
    if not data:
        return False

    try:
        df = pd.DataFrame(data, columns = columns)
        df.to_csv(filename, encoding = 'utf-8-sig', index = False)
        return True
    except Exception as e:
        print(f"Export CSV fail : {e}")
        return False