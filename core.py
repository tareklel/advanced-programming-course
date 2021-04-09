import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import numpy as np
import os
import pandas as pd

from scipy import stats

import matplotlib.pyplot as plt

from save_load import SaveToDatasets, LoadFromDataSets, LoadWindow
from data_transformation import DataTransformation

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


class MainGUI:
    def __init__(self, master):
        self.master = master
        master.title("Main Window")
        master.geometry("700x500")

        # create all elements in main window
        load_csv_button = ttk.Button(self.master,
                                     text='Load CSV Data',
                                     command=lambda: LoadWindow(maingui=self))
        load_db_button = ttk.Button(self.master, text='Load from Datasets',
                                    command=lambda: LoadFromDataSets(maingui=self))
        save_db_button = ttk.Button(master, text='Save Current File to Datasets',
                                    command=lambda: SaveToDatasets(maingui=self))
        data_transform_button = ttk.Button(self.master, text='Data Transformation',
                                           command=self.open_data_transformation)
        data_analysis_button = ttk.Button(self.master, text='Data Analysis',
                                          command=self.open_data_analysis)
        #update later
        preview_df_button = ttk.Button(master, text='Preview Data Frame',
                                       command=lambda: self.update_textbox(self.main_df.head(10)))
        self.text_box = tk.Text(master, bg='grey')

        # insert welcome message into text box and disable
        self.text_box.insert(tk.END, 'Welcome to the Data Analysis Hub')
        self.text_box.config(state='disabled')

        # snap all elements to grid
        load_csv_button.grid(row=0, column=1, padx=(0, 20), sticky='NSEW')
        load_db_button.grid(row=1, column=1, padx=(0, 20), sticky='NSEW')
        save_db_button.grid(row=2, column=1, padx=(0, 20), sticky='NSEW')
        data_transform_button.grid(row=0, column=2, sticky='NSEW')
        data_analysis_button.grid(row=1, column=2, sticky='NSEW')
        preview_df_button.grid(row=2, column=2, sticky='NSEW')
        self.text_box.grid(row=4, column=1, columnspan=2)

        # self.main_df = None
        self.main_df = pd.read_json(os.getcwd()+'/datasets/inspections_sample.json')

    def update_textbox(self, message):
        self.text_box.config(state='normal')
        self.text_box.delete('1.0', 'end')
        self.text_box.insert(tk.END, message)
        self.text_box.config(state='disabled')

    def preview_dataframe(self):
        if self.main_df is not None:
            preview = self.main_df.head(10)
            self.update_textbox(preview)
        else:
            self.update_textbox('No DataFrame loaded')

    def open_data_transformation(self):
        if self.main_df is not None:
            DataTransformation(self)
        else:
            no_dataset = 'No dataset has been loaded'
            messagebox.showerror(title='No dataset', message=no_dataset)

    def open_data_analysis(self):
        if self.main_df is not None:
            DataAnalysis(self)
        else:
            no_dataset = 'No dataset has been loaded'
            messagebox.showerror(title='No dataset', message=no_dataset)


class DataAnalysis(tk.Toplevel):
    def __init__(self, maingui):
        tk.Toplevel.__init__(self)
        self.title("Data Analysis")
        self.geometry("700x700")
        self.maingui = maingui

        # Create descriptive statistics
        per_year = 'Mean, mode and median for the inspection score per year:'
        statistics_label = tk.Label(self, text=per_year)
        stats_options1 = ['for vendor seating', 'for each zip code']
        self.statistics_tkvar1 = tk.StringVar(self)
        statistics_popupmenu1 = ttk.OptionMenu(self, self.statistics_tkvar1,
                                               'for vendor seating', *stats_options1)
        stats_options2 = ['mean', 'mode', 'median']
        self.statistics_tkvar2 = tk.StringVar(self)
        statistics_popupmenu2 = ttk.OptionMenu(self, self.statistics_tkvar2, 'mean',
                                               *stats_options2)
        statistics_button = ttk.Button(self, text='Apply', command=self.get_stats)
        statistics_label.grid(row=1, column=1, columnspan=3, pady=(20, 0), sticky='NSEW')
        statistics_popupmenu1.config(width=15)
        statistics_popupmenu1.grid(row=2, column=1, columnspan=3, sticky='NSEW')
        statistics_popupmenu2.config(width=15)
        statistics_popupmenu2.grid(row=3, column=1, columnspan=1, sticky='NSEW')
        statistics_button.grid(row=3, column=2, columnspan=1, sticky='NSEW')

        # Get the number of establishments that have committed each type of violation
        unique_instance_label = tk.Label(self, text='Get the number of establishments that '
                                                    'have committed each type of violation')
        unique_instance_button = ttk.Button(self, text='Apply', command=self.get_violations)
        unique_instance_label.grid(row=5, column=1, columnspan=3, pady=(20, 0), sticky='NSEW')
        unique_instance_button.grid(row=6, column=1, columnspan=3, sticky='NSEW')

        # Count Average Count of Instances of A grouped by B
        average_count_label = tk.Label(self, text=' Get number of violations committed per vendor '
                                                  'in zip code area')
        average_count_button = ttk.Button(self, text='Apply', command=self.violations_zip)
        average_count_label.grid(row=8, column=1, columnspan=3, pady=(20, 0), sticky='NSEW')
        average_count_button.grid(row=10, column=1, columnspan=3, sticky='NSEW')

        # Add text box
        self.text_box = tk.Text(self, bg='grey')
        self.text_box.insert(tk.END, 'Data analysis updated here')
        self.text_box.config(state='disabled')
        self.text_box.grid(row=11, column=1, columnspan=3, pady=(20, 0), sticky='NSEW')

    def get_stats(self):
        # get mode, median, mean of selected columns
        for_each = {'for vendor seating': 'SEATING',
                    'for each zip code': 'Zip Codes'}
        # get selected index
        for_each_selected = for_each[self.statistics_tkvar1.get()]
        mode = lambda x: stats.mode(x)[0][0]
        stats_dict = {'mean': np.mean, 'mode': mode, 'median': np.median}
        # extract selected statistics function
        stats_selected = stats_dict[self.statistics_tkvar2.get()]

        try:
            result = self.maingui.main_df.pivot_table(index=for_each_selected,
                                                      columns='YEAR',
                                                      values='SCORE',
                                                      aggfunc=stats_selected
                                                      )
            self.update_textbox(f'{self.statistics_tkvar2.get()} for the inspection score '
                                f'per year for {for_each_selected} \n'
                                f'{result}')
        except KeyError as e:
            # show error message if required column is missing
            messagebox.showerror(title='Key error', message=f'{e} column is missing')
            return
        except pd.core.base.DataError as e:
            # show error message if aggregated on non-numeric column
            messagebox.showerror(title='Numeric error', message=e)
            return

    def get_violations(self):
        # Get the number of establishments that have committed each type of violation
        try:
            # get number of unique facilities that committed each violation
            violations = self.maingui.main_df.groupby('VIOLATION DESCRIPTION')['FACILITY NAME'].nunique()
        except KeyError as e:
            messagebox.showerror(title='Key error', message=e)
            return
        # plot the number of facilities that committed each violation
        fig = plt.figure(figsize=(40, 10))
        x = np.arange(len(violations.index))
        plt.xticks(x, violations.index, rotation='vertical')
        plt.title('Number of Establishments that have Committed Each Violation')
        plt.xlabel('Violations')
        plt.ylabel('Number of facilities that committed violation')
        fig.subplots_adjust(bottom=0.683)
        plt.bar(violations.index, violations.values)
        plt.show()

    def violations_zip(self):
        # get the number of violations committed per vendor in zip code area
        try:
            inspections = self.maingui.main_df
            # bin zips into groups of 100
            inspections['Zip Bin'] = np.floor(inspections['Zip Codes']/1000).astype(int)
            zip_mean_violations = inspections[['FACILITY NAME', 'Zip Bin']]\
                .value_counts().groupby('Zip Bin').mean()
            fig, ax = plt.subplots(figsize=(30, 5))
            # create table index and plot on x-axis
            zip_index = [str(int(x)).zfill(2) for x in zip_mean_violations.index]
            x = np.arange(len(zip_mean_violations.index))
            plt.xticks(x, zip_index, rotation='vertical')
            ax.bar(zip_index, zip_mean_violations.values)

            # add mean line
            y_mean = [zip_mean_violations.mean()] * len(x)
            mean_line = ax.plot(x, y_mean, label='Mean', linestyle='--', color='red')
            plt.xlabel('Zip Codes Range')
            plt.ylabel('Average number of violations per facility')
            plt.title('Number of Violations Per Facility in Zip Code')
            plt.legend(handles=mean_line)
            fig.subplots_adjust(bottom=0.256)
            plt.show()

            # get linear coefficients and display
            corr = np.corrcoef(zip_mean_violations.index,
                               zip_mean_violations.values)[0][1]
            self.update_textbox(f'The correlation between Zip Code and '
                                f'number of violations is {corr}')


            del inspections

        except KeyError as e:
            messagebox.showerror(title='Key error', message=e)
            return
        except ValueError as e:
            messagebox.showerror(title='Null Values Detected',
                                 message='Null Values detected,'
                                         ' remove before analysis')

    def update_textbox(self, message):
        self.text_box.config(state='normal')
        self.text_box.delete('1.0', 'end')
        self.text_box.insert(tk.END, message)
        self.text_box.config(state='disabled')


if __name__ == '__main__':
    window = tk.Tk()
    maingui = MainGUI(window)
    window.mainloop()



