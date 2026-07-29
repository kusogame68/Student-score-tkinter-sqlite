# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 00:12:07 2026

@author: Johnson
"""

# Interface Module: 
# - Abstract data-access contract for easier future implementation.
# - See implementations/sqlite_repository.py for the concrete implementation.

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict

class Repository(ABC):
    @abstractmethod
    def open(self) -> bool:
        pass

    @abstractmethod
    def insert(self, values: Dict[str, str]) -> bool:
        pass

    @abstractmethod
    def select_all(self) -> List[Tuple]:
        pass

    @abstractmethod
    def update(self, record_id: int, values: Dict[str, str]) -> bool:
        pass

    @abstractmethod
    def delete(self, record_id: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass