import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import os
import pandas as pd


class SaveToDatasets(tk.Toplevel):
    """
    Widget for saving dataset as JSON file
    in dataset directory
    """
    def __init__(self, maingui):
        tk.Toplevel.__init__(self)
        self.title("Save Current File to Datasets")
        self.geometry("240x200")
        self.maingui = maingui
        self.datadir = os.getcwd()+'/datasets'
        self.filenames = os.listdir(self.datadir)

        filename_label = tk.Label(self, text='Enter filename')
        save_var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=save_var)
        save_button = ttk.Button(self, text='Save as JSON File',
                                 command=self.try_savedataset)

        filename_label.grid(row=0, column=1, sticky='NSEW')
        self.entry.grid(row=1, column=1, sticky='NSEW')
        save_button.grid(row=2, column=1, sticky='NSEW')

    def find_files(self):
        # Check for csvs in path
        files = [x for x in self.filenames if x.endswith('.csv')]
        return files

    def try_savedataset(self):
        # save data set
        self.entry_var = self.entry.get()
        # check if no name was provided for saving
        if self.entry == "":
            no_name = "Please insert a name before saving"
            messagebox.showerror(title='Load error', message=no_name)
            # exit if statement

        # check if dataset is loaded as variable before saving
        elif self.maingui.main_df is None:
            no_dataset = "No dataset loaded to save"
            messagebox.showerror(title='Load error', message=no_dataset)
            # exit if statement
        else:
            # check if entry ends with .json
            if self.entry_var.endswith('.json') is False:
                self.entry_var = self.entry_var+'.json'
            # check if data set exists in directory
            if self.entry_var in self.filenames:
                ReplaceDataset(self)
            #if all other conditions met save dataset
            else:
                self.save_dataset()

    def save_dataset(self):
        self.maingui.main_df.to_json(self.datadir+"/"+self.entry_var)
        # update maingui textbox
        self.maingui.update_textbox(f'{self.entry_var} saved to datasets'
                                    f'directory')
        self.destroy()


class ReplaceDataset(tk.Toplevel):
    """
    Widget with option to overwrite when dataframe with name identical
    to existing JSON file is being saved
    """
    def __init__(self, savetodatasets):
        tk.Toplevel.__init__(self)
        self.title("File Exists")
        self.geometry("300x200")
        self.savetodatasets = savetodatasets
        self.maingui = savetodatasets.maingui

        filename_label = tk.Label(self, text='File exists are you sure you want '
                                             'to overwrite?')
        save_dataset_button = ttk.Button(self, text='Yes',
                                        command=self.save_destroy)
        dont_save_dataset_button = ttk.Button(self, text='No',
                                             command=self.destroy)
        filename_label.grid(row=1, column=1, columnspan=2, sticky='NSEW')
        save_dataset_button.grid(row=2, column=1, sticky='NSEW')
        dont_save_dataset_button.grid(row=2, column=2, sticky='NSEW')

    def save_destroy(self):
        # save dataset and then destroy
        self.savetodatasets.save_dataset()
        # update maingui textbox
        self.maingui.update_textbox(f'{self.savetodatasets.entry_var} '
                                    f'saved to datasets directory')
        self.destroy()


class LoadWindow(tk.Toplevel):
    def __init__(self, maingui):
        tk.Toplevel.__init__(self)
        self.title("Load CSV")
        self.geometry("300x200")
        self.maingui = maingui

        # get csvs in current directory
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.path = os.getcwd()+"/csvs"
        csv_files = self.find_csv_files(self.path)
        for csv in csv_files:
            self.listbox.insert(tk.END, csv)
        self.listbox.grid(row=1, column=1, columnspan=3, sticky='NSEW')

        # assign selected csv to maindf
        load_csv_button = ttk.Button(self, text='Load CSV',
                                     command=self.load_selected)
        load_csv_button.grid(row=2, column=1)

        # clear current dataframe
        clear_df_button = ttk.Button(self, text='Discard DataFrame',
                                     command=self.clear_df)
        clear_df_button.grid(row=2, column=2)

    def find_csv_files(self, path):
        # check for csvs in path
        filenames = os.listdir(path)
        csv_files = [x for x in filenames if x.endswith('.csv')]
        return csv_files

    def load_selected(self):
        active = self.listbox.get(tk.ACTIVE)
        try:
            csv_path = self.path+"/"+active
            main_df = pd.read_csv(csv_path)
            # update maingui variable if maingui is None
            if self.maingui.main_df is None:
                self.maingui.main_df = main_df
            # update maingui status on df loaded
                self.maingui.update_textbox(f'{active} loaded as DataFrame')
                self.withdraw()
            else:
                loaded_prompt = 'Cannot update, another DataFrame is already loaded.'
                'please clear current database first'
                messagebox.showerror(title='Load error', message=loaded_prompt)
        except pd.errors.ParserError:
            error = 'Looks like you either have no csvs in working directory ' \
                   'or loaded a file that is not a csv, please try another file'
            messagebox.showerror(title='Load error', message=error)

    def clear_df(self):
        self.maingui.main_df = None
        self.maingui.update_textbox('DataFrame removed, none loaded')


class LoadFromDataSets(tk.Toplevel):
    def __init__(self, maingui):
        tk.Toplevel.__init__(self)
        self.title("Load From Data Base")
        self.geometry("200x200")
        self.maingui = maingui
        self.path = os.getcwd()+"/datasets"

        json_files = self.find_json_files()
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        for file in json_files:
            self.listbox.insert(tk.END, file)
        self.listbox.grid(row=1, column=1, columnspan=3, sticky='NSEW')

        load_db_button = ttk.Button(self, text='Load Table',
                                    command=self.load_selected)
        load_db_button.grid(row=2, column=1, sticky='NSEW')

        # clear current dataframe
        clear_df_button = ttk.Button(self, text='Discard DataFrame',
                                     command=self.clear_df)
        clear_df_button.grid(row=2, column=2)

    def find_json_files(self):
        # check for json files in path
        filenames = os.listdir(self.path)
        json_files = [x for x in filenames if x.endswith('.json')]
        return json_files

    def load_selected(self):
        active = self.listbox.get(tk.ACTIVE)
        try:
            json_path = self.path+"/"+active
            main_df = pd.read_json(json_path)
            # update maingui variable if maingui is None
            if self.maingui.main_df is None:
                self.maingui.main_df = main_df
            # update maingui status on df loaded
                self.maingui.update_textbox(f'{active} loaded as DataFrame')
                self.withdraw()
            else:
                loaded_prompt = 'Cannot update, another DataFrame is already loaded.'
                'please clear current database first'
                messagebox.showerror(title='Load error', message=loaded_prompt)
        except pd.errors.ParserError:
            error = 'Looks like you either have no json files in working directory ' \
                   'or loaded a file that is not a json, please try another file'
            messagebox.showerror(title='Load error', message=error)

    def clear_df(self):
        self.maingui.main_df = None
        self.maingui.update_textbox('DataFrame removed, none loaded')
