# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 23:24:14 2023

@author: Johnson
"""

import sqlite3
import tkinter as tk
import tkinter.messagebox as msg
import pandas as pd
import os 

# db
class StudentsDatabase:
    def __init__(self):
        self.table_index = ('id','學號','姓名','國文','英文','數學','平均分')
        self.db_name='學生成績建檔系統.db'
        self.table_name='person'
        self.conn=None
        self.cur = None
        self.index_lengh=len(self.table_index)
        self.table_index_rep=f'{self.table_index[1:]}'.replace('[', '').replace(']', '').replace("'", '')
    
    # 總排名/科排名..
    def select_over_2(self):
        it=iter(self.table_index)
        self.table_str=self.table_str.format(self.table_name,next(it),next(it))
        self.table_str=self.table_str[:-2]+','
        # 2
        devide7=self.index_lengh-2
        # 進行 (table_name,iter集合)[n]後的運算
        more_table_str=','.join([f"\n'{next(it)}' TEXT" for i in range(devide7)])
        self.table_str+=more_table_str+');'
        # 釋放記憶體
        del it,devide7,more_table_str
    
    def select_with_2(self):
        # {'name0':'id','name1':'學號'...}
        data={f"name{index}": index_name for index, index_name in enumerate(self.table_index)} 
        self.table_str=self.table_str.format(self.table_name,data["name0"],data["name1"])
        del data
    
    def select_under_2(self):
        raise IndexError('table_index不能小於2個')
    
    # 多欄位篩選 
    def get_table_str(self):
        self.table_str="""CREATE TABLE if not exists '{}'(
                        '{}' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                        '{}' TEXT UNIQUE NOT NULL);"""
        if self.index_lengh>2:
            self.select_over_2()
        elif self.index_lengh==2:
            self.select_with_2()
        else:
            self.select_under_2()
        return self.table_str
   
    # 開啟
    def db_open(self):
        try:
            # 資料庫不存在會新增
            with sqlite3.connect(self.db_name) as self.conn:
                self.cur=self.conn.cursor()
            # 執行sql指令
                self.cur.execute(self.get_table_str())
                self.conn.commit()               
        except Exception as e:
            print(e)
    
    # 寫入
    def db_write(self,entrys_get):
        if self.conn is not None:
            try:
                self.values=entrys_get
                placeholder_rep=f'{tuple("?" for i in range(len(self.table_index[1:])))}'.replace("'",'')
                sql=f"INSERT INTO {self.table_name} {self.table_index_rep} values{placeholder_rep};"
                self.conn.execute(sql,self.values)
                self.conn.commit()
                del placeholder_rep,sql
            except Exception as e:
                self.conn.rollback()
                print(e)
                
    # 查詢
    def db_select(self):
        if self.conn is not None:
            try:
                sql=f'SELECT * FROM {self.table_name};'
                self.list=list(self.cur.execute(sql))
                return self.list
            except Exception as e:
                self.conn.rollback()
                print(e)
    
    # 修改
    def db_update(self,data):
        if self.conn is not None:
            try:
                sql=f'UPDATE {self.table_name} SET '
                sql+=data
                self.conn.execute(sql)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                print(e)
    
    # 刪除
    def db_delete(self,state=0,data=None):
        if self.conn is not None:
            try:
                if data!=None:
                    if state==1:
                        sql=f'DELETE FROM {self.table_name} where {self.table_index[0]} is {data};'
                    else:
                        sql=f'DELETE FROM {self.table_name} where {self.table_index[1]} is {data};'
                else:
                    sql=f'DELETE FROM {self.table_name};'
                self.cur.execute(sql)
                self.conn.commit()
                del sql
            except Exception as e:
                self.conn.rollback()
                print(e)

    # 關閉
    def db_close(self):
        if self.conn is not None:
            try:
                self.conn.close()
                self.conn,self.cur=None,None
            except Exception as e:
                self.conn.rollback()
                print(e)

# tk            
class StudentsTkinter(StudentsDatabase):       
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
        
    # 建構tkinter    
    def get_win(self):
        self.win=tk.Tk()
        self.win.title(self.title)
        self.win.geometry(self.geometry)
        self.win.resizable(self.resizable,self.resizable)
        self.win.iconbitmap(self.iconbitmap)
        self.interface()
        self.win.mainloop()
        
    # 建構GUI介面
    def interface(self):       
        self.font0=("微軟正黑體",12)
        self.font1=("標楷體",24)
        self.font2=("標楷體",16)
        self.font3=("標楷體",14)
        # listbox_var
        self.list_var=tk.StringVar()
        
        # ('學號', '姓名', '國文', '英文', '數學')
        self.ety_ind=tuple(filter(lambda x: x in self.table_index[1:] and '平均分' not in x,self.table_index))
        
        # frame
        self.creat_frame()
        # frame0
        self.label0=tk.Label(self.frame0,text=f'歡迎使用 {self.title}',bg='black',fg='white',anchor='w')
        self.label0.pack(expand=1,fill='x')
        
        # frame1 
        self.get_frame1()
        
        # frame2
        self.get_frame2()
        
        # frame3
        self.listbox=tk.Listbox(self.frame3,listvariable=self.list_var)
        self.listbox.pack(fill='both',expand=1)
    
    def creat_frame(self):
        self.frame0=tk.Frame(self.win,bg='black')
        self.frame1=tk.Frame(self.win,)
        self.frame2=tk.Frame(self.win,bg='#d2b48c')
        self.frame3=tk.Frame(self.win,bg='white')
        
        self.frame0.pack(fill='x')
        self.frame1.pack(fill='x')
        self.frame2.pack(fill='x')
        self.frame3.pack(fill='x')
    
    # 創建frame1
    def get_frame1(self):
        # self.entrys={'學號':tk.Entry...}
        self.entrys={}
        labels=tuple([f'{self.title}']+list(self.ety_ind))
        for i in range(len(labels)):
            if i==0:
                self.label=tk.Label(self.frame1,text=f'{self.title}',font=self.font1).grid(row=0,column=0,columnspan=2,padx=10,pady=5)
            else:
                self.label=tk.Label(self.frame1,text=labels[i],font=self.font3).grid(row=i,column=0,padx=5,pady=2)
                self.entrys[self.ety_ind[i-1]]=tk.Entry(self.frame1,bg="lightyellow",fg="black",font=self.font3,borderwidth=3)
                self.entrys[self.ety_ind[i-1]].grid(row=i,column=1,pady=10)
        self.entrys=pd.Series(self.entrys,dtype=object)
        del labels
        
    # 創建frame2
    def get_frame2(self):
        self.btns={}
        labels=('新增','查詢','修改','刪除','開啟','結束')
        com=(self.tk_write,self.tk_select,self.tk_update,self.tk_delete,self.tk_open,self.tk_close)
        for i in range(len(labels)):
            self.btns[labels[i]]=tk.Button(self.frame2,text=labels[i],font=self.font2,command=com[i])
            if i==4:
                self.btns[labels[i]].grid(row=1,column=0,columnspan=2,padx=5,pady=5,sticky='nswe')
            elif i==5:
                self.btns[labels[i]].grid(row=1,column=2,columnspan=2,padx=5,pady=5,sticky='nswe')
            else:
                self.btns[labels[i]].grid(row=0,column=i,padx=5,pady=5,sticky='nswe')
        del labels,com   
    
    # 匯入csv
    def creat_csv(self):
        if self.conn is not None:
            try:
                if len(super().db_select())==0:
                    return
                selectfile=super().db_select()
                getfile=pd.DataFrame(selectfile,columns=self.table_index)
                getfile['總分']=getfile[list(self.table_index[3:6])].astype(int).sum(axis=1)
                if '平均分' not in getfile.columns:
                    getfile['平均分']=getfile[list(self.table_index[3:6])].astype(int).mean(axis=1)
                getfile['評級']=getfile[self.table_index[6]].astype(float).astype(int).apply(__class__.get_level)
                getfile.to_csv(self.db_name.replace('.db','.csv'),encoding='utf-8-sig',index=False)
                del selectfile,getfile
            except Exception as e:
                print(e)
    
    @classmethod
    def get_level(cls,avg):
        if avg>=60:
            if avg>=100:
                return 'A'
            elif avg>=90:
                return 'B'
            elif avg>=80:
                return 'C'
            elif avg>=70:
                return 'D'
            else:
                return 'E'
        else:
            return 'F'
    
    def any_info_yet(self,key='yes'):
        key=key.lower()
        if key=='yes'.lower():
            self.label0.config(text='No data!',fg='pink')
            msg.showwarning(title='Warning',message='目前無資料!')
        else:
            self.label0.config(text='Not found file!',fg='red')
            msg.showwarning(title='Warning',message='查無此資料!')
    
    def msg_open_success(self,key='yes'):
        key=key.lower()
        if key=='yes':
            self.label0.config(text='Open data success!',fg='green')
        elif key=='oops':
            self.label0.config(text='Open Already!',fg='pink')
            msg.showwarning(title='Warning',message='檔案狀態 : 開啟中!')
        elif key=='yet':    
            self.label0.config(text='Open not yet!',fg='pink')
            msg.showwarning(title='Warning',message='請先點選「開啟」按鈕!')
        else:
            self.label0.config(text='Open data fail!',fg='red')
            msg.showerror(title='Error',message='開啟失敗!')
            
    def msg_write_success(self,key='yes'):
        key=key.lower()
        if key=='yes':
            self.label0.config(text='Add data success!',fg='green')
            msg.showinfo(title='Information',message=f'{self.c} \n寫入成功!') 
        elif key=='oops':
            msg.showerror(title='Error', message='請輸入完整資料!')
        elif key=='repeat':
            self.label0.config(text='Add data already!',fg='red')
            msg.showwarning(title='Warning',message='資料已經寫入，請重新輸入!')
        else:
            self.label0.config(text='Add data fail!',fg='red')
            msg.showerror(title='Error',message='輸入資料有誤!')
    
    def msg_update_success(self,key='yes'):
        key=key.lower()
        if key=='yes':
            self.label0.config(text='Update data success!',fg='green')
            msg.showinfo(title='Information',message='資料已修改!') 
        elif key=='oops':
            msg.showwarning(title='Warning',message='請輸入需要更新的資料!') 
        elif key=='keyisnull':
            msg.showwarning(title='Warning',message='請輸入需要更新的對象!') 
        else:
            self.label0.config(text='Update fail!',fg='red')
            msg.showerror(title='Warning',message='修改失敗!')
            
    def msg_delete_success(self,key='yes'):
        key=key.lower()
        if key=='yes':
            self.label0.config(text='Delete data success!',fg='green')
            msg.showinfo(title='Information',message='資料已刪除!')
        else:
            self.label0.config(text='Delete fail!',fg='red')
            msg.showerror(title='Warning',message='刪除失敗!')
            
    def show_len_file(self):
        self.label0.config(text=f'Have {len(list(super().db_select()))} datas!',fg='green')
        msg.showinfo(title='Information',message=f'目前有{len(super().db_select())}筆資料!')
    
    # 確認空值數量
    def count_null(self):
        count=sum(1 for entry in self.entrys[1:] if entry.get()=='')
        target=len(self.ety_ind)-1
        if count==target:
            return 'same'
        else:
            return 'pass'
        
    # 確認conn狀態    
    def check_conn_state(self):
        if self.conn is None:
            return 'yet'
        else:
            return 'open'
    
    # 開啟
    def tk_open(self):
        if self.check_conn_state()=='open':
            self.msg_open_success('oops')
            return
        try:
            super().db_open() 
            self.tk_select('refresh')
            self.msg_open_success('yes')
        except Exception as e:
            self.msg_open_success('no')
            print(e)
            
    # 寫入
    def tk_write(self):
        if self.check_conn_state()=='yet':
            self.msg_open_success('yet')
            return
        try:
            if any(i.get()=='' for i in self.entrys):
                return self.msg_write_success('oops')
            # 算平均分
            entrys_get=self.write_decide()
            # 檢測是否寫入過
            if self.tk_select('check_repeat')=='repeat':
                return self.msg_write_success('repeat')
            # 將entry參數傳給父類
            self.db_write(entrys_get)
            self.tk_select('refresh')
            self.msg_write_success('yes')
            del entrys_get
        except Exception as e:
            self.msg_write_success('no')
            print(e)
            
    def write_decide(self):
        avg=round(pd.Series((eval(self.entrys[2].get()),eval(self.entrys[3].get()),eval(self.entrys[4].get()))).mean(),1)
        entrys_get=(tuple([i.get() for i in self.entrys]+[avg]))
        self.c='\n'.join(f'{self.ety_ind[i]}:{entrys_get[i]},' for i in range(len(self.ety_ind)))
        del avg
        return entrys_get
      
    # 查詢
    def tk_select(self,state=0):
        if self.check_conn_state()=='yet':
            self.msg_open_success('yet')
            return
        try:
            self.list_var.set(self.db_select())
            # 不要有任何動作
            if state=='refresh':
                pass
            elif state=='check_repeat':
                if self.entrys[0].get() in (i[1] for i in super().db_select()):
                    return 'repeat'
                elif self.entrys[0].get() not in (i[1] for i in super().db_select()):
                    return 'notfound'
            elif state=='len_is_zero':
                if len(super().db_select())==0:
                    return 'yes'
            else:
                self.show_len_file()
        except Exception as e:
           print(e)
    

    def tk_update(self):
        if self.check_conn_state()=='yet':
            self.msg_open_success('yet')
            return
        try:
            if self.update_rules()=='break':
                return
            if self.listbox.curselection()!=():
                merge_sql=self.update_decide_curselection_notnull()
            else:
                if self.update_decide_curselection_isnull()=='notfound':
                    self.any_info_yet('no')
                    return
                merge_sql=self.update_decide_curselection_isnull()
            super().db_update(merge_sql)
            self.tk_select('refresh')
            self.msg_update_success('yes')
            del merge_sql
        except Exception as e:
            self.msg_update_success('no')
            print(e)
    
    def update_rules(self):
        # len=0
        if self.tk_select('len_is_zero')=='yes':
            self.any_info_yet('yes')
            return 'break'
        # 確認空值數量
        elif self.count_null()=='same':
            self.msg_update_success('oops')
            return 'break'
        elif self.listbox.curselection()==() and self.entrys[0].get()=='':
            self.msg_update_success('keyisnull')
            return 'break'
    
    def update_decide_curselection_notnull(self):
        numbers=[]
        merge_sql=''
        self.select=self.listbox.curselection()[0]
        #0.1.2.3..
        for i in range(len(self.entrys[1:])):
            if self.entrys[1:][i].get()!='':
                merge_sql+=f'{self.table_index[i+2]}={self.entrys[1:][i].get()} ,'
                if i!=0:numbers.append(eval(self.entrys[1:][i].get()))
            else:
                merge_sql+=f'{self.table_index[i+2]}={self.listbox.get(self.select)[i+2]} ,'
                if i!=0:numbers.append(eval(self.listbox.get(self.select)[i+2]))
        avg=round(pd.Series(numbers).mean(),1)
        merge_sql+=f'平均分={avg} where {self.table_index[0]} is {self.listbox.get(self.select)[0]};'
        del numbers,avg
        return merge_sql
    
    def update_decide_curselection_isnull(self):
        if self.entrys[0].get()!='':
            if self.tk_select('check_repeat')=='notfound':
                return 'notfound'
            numbers=[]
            merge_sql=''
            for i in range(len(self.entrys[1:])):
                if self.entrys[1:][i].get()!='':
                    merge_sql+=f'{self.table_index[i+2]}={self.entrys[1:][i].get()} ,'
                    if i!=0:numbers.append(eval(self.entrys[1:][i].get()))
                else:
                    key_select=tuple(filter(lambda x: self.entrys[0].get() in x,super().db_select()))
                    key_result=tuple(i for i in key_select if i[1]==self.entrys[0].get())
                    merge_sql+=f'{self.table_index[i+2]}={key_result[0][i+2]} ,'
                    if i!=0:numbers.append(eval(key_result[0][i+2]))
            avg=round(pd.Series(numbers).mean(),1)
            merge_sql+=f'平均分={avg} where {self.ety_ind[0]} is {self.entrys[0].get()};'  
            del numbers,avg
            return merge_sql
    
    # 刪除
    def tk_delete(self):
        if self.check_conn_state()=='yet':
            self.msg_open_success('yet')
            return
        try:
            if self.tk_select('len_is_zero')=='yes'.lower():
                self.any_info_yet('yes')
                return
            self.delete_decide()
            self.tk_select('refresh')
            self.msg_delete_success('yes')
        except Exception as e:
            self.msg_delete_success('no')
            print(e)
            
    def delete_decide(self):
        # listbox如果有選取
        # listbox1.curselection() => 沒選()
        if self.listbox.curselection()!=():
            # 選取到的位置(1,) => 代表點選第一個，使用[0]位置取id值
            self.select=self.listbox.curselection()[0]
            # 取得該筆資料,以[0]取id進行刪除
            super().db_delete(1,self.listbox.get(self.select)[0])
        elif self.entrys[0].get()!='': 
            if self.tk_select('check_repeat')=='notfound'.lower():
                self.any_info_yet('no')
                return
            super().db_delete(2,self.entrys[0].get())
        elif self.entrys[0].get()=='':
            if msg.askquestion(title='Question',message='資料將會全部刪除,\n確定嗎?')!='YES'.lower():
                return
            super().db_delete()        

    # 關閉    
    def tk_close(self):
        self.creat_csv()
        super().db_close()
        self.win.destroy()
        
class LoginView(StudentsTkinter):
    # 文字樣式
    font=("標楷體",14)
    def __init__(self,title='Login',geometry='300x200',resizable=False,iconbitmap=None):
        # 存取父類init屬性
        super().__init__()
        self.title=title
        self.geometry=geometry
        self.resizable=resizable
        self.iconbitmap=iconbitmap
        self.win=self.get_win()
        
    # 建構GUI介面
    def interface(self):       
        # frame
        self.frame0=tk.Frame(self.win)
        self.frame0.pack(expand=1,fill='both')
        
        # frame0
        self.label0=tk.Label(self.frame0,text='帳號:',font=LoginView.font).pack(expand=1)
        self.entry0=tk.Entry(self.frame0,justify='center',font=LoginView.font)
        self.entry0.pack(expand=1)
        self.label1=tk.Label(self.frame0,text='密碼:',font=LoginView.font).pack(expand=1)
        self.entry1=tk.Entry(self.frame0,justify='center',show='*',font=LoginView.font)
        self.entry1.pack(expand=1)
        self.button=tk.Button(self.frame0,text='登入',font=LoginView.font,command=self.login)
        self.button.pack(expand=1)

    def msg_login_success(self,key='yes'):
        key=key.lower()
        if key=='yes':
            msg.showinfo(title='Success',message='登入成功!')
        else:
            msg.showerror(title='Fail',message='登入失敗!')

    def login(self):
        try:
            # 確認帳號數量是否>0
            if not os.path.exists('登入系統.db'):
                self.any_info_yet('yes')
                return 
            if self.get_account_with_match()=='success':
                self.msg_login_success('yes')
                self.win.destroy()
                self.run_main_program()
                return 
            else:
                self.msg_login_success('no')
                return 
        except Exception as e:
            print(e)            
    
    def get_account_with_match(self):
        with sqlite3.connect('登入系統.db') as conn:
            cur=conn.cursor()
            sql=f'SELECT * FROM {self.table_name};'
            self.list=cur.execute(sql)
            if any(i[1] == self.entry0.get() and i[2] == self.entry1.get() for i in self.list):
                return 'success'
              
    def run_main_program(self):
        st=StudentsTkinter(iconbitmap=r'..\Image\person.ico')
        st.get_win()
        
if __name__=='__main__':
    lv=LoginView(iconbitmap=r'..\Image\login.ico')
    lv
    