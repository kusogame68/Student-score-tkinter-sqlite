# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 07:27:37 2023

@author: Johnson
"""

from StudentsScoreSystem import StudentsDatabase as sd
from StudentsScoreSystem import StudentsTkinter as st
import pandas as pd

class CreatAccountDatabase(sd):
    def __init__(self):
        super().__init__()
        self.db_name='登入系統.db'
        self.table_index=('id','帳號','密碼')
        self.index_lengh=len(self.table_index)
        self.table_index_rep=f'{self.table_index[1:]}'.replace('[', '').replace(']', '').replace("'", '')
        
class CreatAccountTkinter(CreatAccountDatabase,st):
    def __init__(self,title=None,geometry=None,resizable=False,iconbitmap=None):
        # 存取父類init屬性
        super().__init__()
        if title==None:
            self.title=self.db_name[:-3]
        else:
            self.title=title
        self.geometry=geometry
        self.resizable=resizable
        self.iconbitmap=iconbitmap
        self.ety_ind=tuple(filter(lambda x: x in self.table_index[1:],self.table_index))
        self.win=self.get_win()
            
    def write_decide(self):
        entrys_get=tuple(i.get() for i in self.entrys)
        self.c='\n'.join(f'{self.ety_ind[i]}:{entrys_get[i]},' for i in range(len(self.ety_ind)))
        return entrys_get

    def update_decide_curselection_notnull(self):
        self.select=self.listbox.curselection()[0]
        merge_sql=f'{self.table_index[2]}={self.entrys[1].get()} where {self.table_index[0]} is {self.listbox.get(self.select)[0]};'
        return merge_sql
    
    def update_decide_curselection_isnull(self):
        if self.entrys[0].get()!='':
            if self.tk_select('check_repeat')=='notfound':
                return 'notfound'
            merge_sql=f'{self.table_index[2]}={self.entrys[1].get()} where {self.ety_ind[0]} is {self.entrys[0].get()};'
            return merge_sql

    def creat_csv(self):
        if self.conn is not None:
            try:
                if len(super().db_select())==0:return
                selectfile=super().db_select()
                getfile=pd.DataFrame(selectfile,columns=self.table_index)
                getfile.to_csv(self.db_name.replace('.db','.csv'),encoding='utf-8-sig',index=False)
                del selectfile,getfile
            except Exception as e:
                print(e)
        
if __name__=='__main__':
    ct=CreatAccountTkinter(iconbitmap=r'..\Image\login.ico')
    ct