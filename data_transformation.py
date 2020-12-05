import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import re
import os
import pandas as pd
import numpy as np
from dateutil.parser import parse


class DataTransformation(tk.Toplevel):
    def __init__(self, maingui):
        tk.Toplevel.__init__(self)
        self.title("Data Transformation")
        self.geometry("700x1000")
        self.maingui = maingui

        # create filter data section
        filter_label = tk.Label(self, text='Filter Data')
        self.cols = self.maingui.main_df.columns
        self.filter_var1 = tk.StringVar()
        self.filter_var1.set(self.cols[0])
        self.filter_popupmenu1 = ttk.OptionMenu(self, self.filter_var1,
                                                self.cols[0], *self.cols)
        self.filter_popupmenu1.config(width=30)

        self.filter_var2 = tk.StringVar(self)
        self.var2_options = self.maingui.main_df[self.filter_var1.get()].unique()
        self.filter_var2.set(self.var2_options[0])
        self.filter_var1.trace('w', self.update_options)
        self.filter_popupmenu2 = ttk.OptionMenu(self, self.filter_var2,
                                                self.var2_options[0],
                                                *self.var2_options)
        self.filter_popupmenu2.config(width=30)
        filter_button = ttk.Button(self, text='Apply', command=self.filter_data)
        filter_label.grid(row=1, column=1, columnspan=3, pady=(20, 0), sticky='NSEW')
        self.filter_popupmenu1.grid(row=2, column=1, columnspan=3, sticky='NSEW')
        self.filter_popupmenu2.grid(row=3, column=1, columnspan=3, sticky='NSEW')
        filter_button.grid(row=3, column=6, columnspan=1, sticky='NSEW')

        # remove duplicates
        remove_dups_label = tk.Label(self, text='Remove Duplicates')
        remove_dups_button = ttk.Button(self, text='Apply',
                                        command=self.drop_duplicates)
        remove_dups_label.grid(row=7, column=1, columnspan=3,
                               pady=(20, 0), sticky='NSEW')
        remove_dups_button.grid(row=8, column=1, columnspan=3, sticky='NSEW')

        # remove content and extract to new column
        remove_extract_label = tk.Label(self, text='Extract Seating from '
                                                   'PE DESCRIPTION to New Column')
        remove_extract_button = ttk.Button(self, text='Apply',
                                           command=self.extract_seating)
        remove_extract_label.grid(row=9, column=1, columnspan=3,
                                  pady=(20, 0), sticky='NSEW')
        remove_extract_button.grid(row=10, column=1, columnspan=3, sticky='NSEW')

        # Join table to another table in the database
        join_tables_label = tk.Label(self, text='Join with Other Table')
        self.join_tables_tkvar1 = tk.StringVar(self)
        self.jsonpath= os.getcwd()+"/datasets"
        filenames = os.listdir(self.jsonpath)
        json_files = [x for x in filenames if x.endswith('.json')]
        join_tables_optionmenu1 = ttk.OptionMenu(self, self.join_tables_tkvar1, *json_files)
        join_tables_optionmenu1.config(width=30)
        self.join_tables_tkvar2 = tk.StringVar(self)
        options = ['inner', 'left', 'right']
        join_tables_optionmenu2 = ttk.OptionMenu(self, self.join_tables_tkvar2, *options)
        join_tables_optionmenu2.config(width=30)
        self.join_tables_tkvar3 = tk.StringVar(self)
        join_tables_popupmenu3 = ttk.OptionMenu(self, self.join_tables_tkvar3, *self.cols)
        join_tables_popupmenu3.config(width=30)
        join_tables_button = ttk.Button(self, text='Apply', command=self.join_tables)
        join_tables_label.grid(row=13, column=1, columnspan=3, pady=(20, 0), sticky='NSEW')
        join_tables_optionmenu1.config(width=15)
        join_tables_optionmenu1.grid(row=14, column=1, columnspan=1, sticky='NSEW')
        join_tables_optionmenu2.config(width=15)
        join_tables_optionmenu2.grid(row=14, column=3, columnspan=1, sticky='NSEW')
        join_tables_popupmenu3.grid(row=15, column=1, columnspan=3, sticky='NSEW')
        join_tables_button.grid(row=16, column=3, columnspan=1, sticky='NSEW')

        # Create year column
        year_label = tk.Label(self, text='Extract Year')
        year_button = ttk.Button(self, text='Apply',
                                 command=self.year_col)
        year_label.grid(row=17, column=1, columnspan=3,
                        pady=(20, 0), sticky='NSEW')
        year_button.grid(row=18, column=1, columnspan=3, sticky='NSEW')

        # Add text box
        self.text_box = tk.Text(self, bg='grey')
        self.text_box.insert(tk.END, 'Data transformation updates show here')
        self.text_box.config(state='disabled')
        self.text_box.grid(row=21, column=1, columnspan=3, pady=(20, 0), sticky='NSEW')

    def update_options(self, *args):
        # update option in second option menu when first option selected
        self.var2_options = self.maingui.main_df[self.filter_var1.get()].unique()
        self.filter_var2.set(self.var2_options[0])
        self.filter_popupmenu2['menu'].delete(0, 'end')
        for unique in self.var2_options:
            self.filter_popupmenu2['menu'].add_command(
                label=unique, command=lambda value=unique: self.filter_var2.set(value)
            )

    def filter_data(self):
        # remove selected value
        column = self.filter_var1.get()
        value = self.filter_var2.get()
        # change numerical dtypes into float or integer
        if self.maingui.main_df[column].dtypes.name == 'float64':
            value = float(value)
        elif self.maingui.main_df[column].dtypes.name == 'int64':
            value = int(value)
        try:
            condition = self.maingui.main_df[column] != value
            self.maingui.main_df = self.maingui.main_df[condition]
            self.update_options()
            self.update_textbox(f'rows with {value} in {column} column removed')
        except IndexError:
            messagebox.showerror(title='Out of Bounds',
                                message='No columns are left to remove')

    def join_tables(self):
        try:
            # load table from JSON directory
            json_file = self.join_tables_tkvar1.get()
            table = pd.read_json(self.jsonpath+"/"+json_file)
            # define join method and column
            how = self.join_tables_tkvar2.get()
            col = self.join_tables_tkvar3.get()
            # assign joined df to main_df
            self.maingui.main_df = pd.merge(self.maingui.main_df,
                                            table,
                                            how=how,
                                            on=col)
            self.update_textbox(f'Loaded DataFrame joined with {json_file} '
                                f'on {col} using {how} join')
        except KeyError as e:
            col_not_common = 'Selected column does not exist in joining table'
            messagebox.showerror(title=f'{e} Column does not exist', message=col_not_common)
        except ValueError:
            value_error = 'Chosen file is not JSON'
            messagebox.showerror(title=f'Chosen file is not JSON', message=value_error)

    def drop_duplicates(self):
        size_before = self.maingui.main_df.size
        self.maingui.main_df = self.maingui.main_df.drop_duplicates()
        size_after = self.maingui.main_df.size
        if size_before == size_after:
            self.update_textbox('No duplicates were found')
        if size_before > size_after:
            diff = size_before - size_after
            self.update_textbox(f'{diff} duplicate rows dropped')

    def extract_seating(self):
        if 'SEATING' in self.maingui.main_df.columns:
            messagebox.showerror(title="SEATING Column Exists",
                                 message="SEATING column already exists")
            return
        try:
            # extract content inside parantheses
            in_paran = lambda x: self.extract_content(x)
            self.maingui.main_df['SEATING'] = self.maingui.main_df['PE DESCRIPTION']\
                .apply(in_paran)
            # extract content outside parantheses
            no_paran = lambda x: " ".join(re.findall(r"(.*?)(?:\(.*?\)|$)", x))
            self.maingui.main_df['PE DESCRIPTION'] = self.maingui.main_df['PE DESCRIPTION']\
                .apply(no_paran)
            # update list of columns in tables
            self.update_columns()
            self.update_textbox(f'SEATING column created')
        except KeyError as e:
            error = f'{e} column does not exist in loaded dataframe'
            messagebox.showerror(title='No dataset', message=error)

    def extract_content(self, string):
        # extract content between parentheses otherwise return not specified
        try:
            return re.search(r'\((.*?)\)', string).group(1)
        except AttributeError:
            return "Not Specified"

    def update_columns(self):
        self.cols = self.maingui.main_df.columns
        self.filter_popupmenu1['menu'].delete(0, 'end')
        for unique in self.cols:
            self.filter_popupmenu1['menu'].add_command(
                label=unique, command=lambda value=unique: self.filter_var1.set(value)
            )

    def update_textbox(self, message):
        # update textbox when transformation is applied
        self.text_box.config(state='normal')
        self.text_box.delete('1.0', 'end')
        self.text_box.insert(tk.END, message)
        self.text_box.config(state='disabled')

    def year_col(self):
        if 'YEAR' in self.maingui.main_df.columns:
            messagebox.showerror(title="YEAR Column Exists",
                                 message="YEAR column already exists")
            return
        try:
            self.maingui.main_df['YEAR'] = self.maingui.main_df['ACTIVITY DATE']\
                .apply(lambda x: parse(x, fuzzy=True).year)
            self.update_columns()
            self.update_textbox('YEAR column added')
        except KeyError as e:
            messagebox.showerror(title=f'No {e} Column',
                                 message=f'No {e} column found')
