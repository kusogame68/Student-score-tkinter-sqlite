# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 00:12:07 2026

@author: Johnson
"""

# Interface Module:
# - Abstract UI contract for easier future implementation.
# - See implementations/tk_management_view.py for the concrete implementation.

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Callable

class View(ABC):
    @abstractmethod
    def bind_commands(self, commands: Dict[str, Callable]) -> None:
        pass

    @abstractmethod
    def get_form_data(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_selected(self) -> Optional[Tuple]:
        pass

    @abstractmethod
    def refresh_list(self, data: List[Tuple]) -> None:
        pass

    @abstractmethod
    def set_status(self, text: str, color: str = 'green') -> None:
        pass

    @abstractmethod
    def show_info(self, message: str) -> None:
        pass

    @abstractmethod
    def show_warning(self, message: str) -> None:
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        pass

    @abstractmethod
    def ask_confirm(self, message: str) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass