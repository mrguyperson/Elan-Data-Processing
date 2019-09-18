# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 11:38:41 2019

@author: Ted
"""

import pandas as pd
import re
import numpy as np

# read .csv file in
def readData():
    while True:
        response = str(input('Is your file saved in the same directory as this script? (Y/N) -> '))
        
        if response == 'Y':
            fileName = str(input('What is the file name (including .csv) -> '))
            break
        elif response == 'N':
            fileName = str(input('What is the full path of your file? -> '))
            break
        else:
            print('Please respond with "Y" or "N".')
        
    data = pd.read_csv(fileName,header=None)
    # Replace double space with 'NaN' in the first column
    data[:][0] = data[:][0].replace(r'^\s*$', np.nan, regex=True)

    return data

""" TO DO : make num_rows check for input type; e.g., if it's an integer or not """


""" selection of rows that contain log information """

def selectLogRows(log_rows):
    logs = (data[:][0].str.contains('^Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday.*',
            flags=re.I, regex=True) == True).fillna(False)
    for row in list(range(1,log_rows)):
        log_start = (data[:][0].str.contains('^Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday.*',
                     flags=re.I, regex=True) == True).fillna(False)
        logs |= log_start.shift(row)
        logs.append(logs)
    return logs  


""" deal with log rows: delete log rows from data file, select sample names, export log data """
def logOutput():
    num_rows = int(input('How many log rows are there? ->'))
    # log rows to delete
    logs = selectLogRows(num_rows)

    # add bolean logs' column to dataframe
    data['logs'] = logs
      
    # get sample names using selectLogRows function
    sample_log = selectLogRows(0)
    sample_log |= sample_log.shift(-1)

    # add bolean 'sample logs' column to dataframe
    data['sample log'] = sample_log

    # create a dataframe of log data to export
    log_export = pd.DataFrame(data[0].loc[(data['sample log'] == True) | (data['logs'] == True)])
    return log_export

def cleanAndExportData():
    # remove rows with log data by creating new dataframe
    data_new = data.loc[data.logs == False]

    """ create column for sample names """
    
    # prevents 'SettingWithCopyWarning'
    data_new = data_new.copy()
    
    # adds new column with values from column [0] that are 'True' in the 'sample log' column
    data_new['sample names'] = data[0].loc[data['sample log'] == True]
    
    """ remove unnecessary columns, and rearrange and relabel remaining columns """
    
    # create list of column names
    cols = list(data_new.columns.values)
    
    # reorganize columns and remove unnecessary columns
    data_new = data_new[[cols[-1]] +cols[0:4]]
    
    # rename columns
    data_new.columns = ['Sample ID', 'Replicate', 'Element', 'Mass', 'CPS']
        
    """ filling empty cells with sample ID's and replicate numbers """
    
    # Fill empty Sample ID cells with appropriate sample name
    data_new[['Sample ID']] = data_new[['Sample ID']].fillna(method='ffill')
    
    # Create column 'Same' highlighting where the sample ID appears in Replicate
    data_new['Same'] = data_new['Sample ID'] == data_new['Replicate']

    # Delete rows where sample name appears in Replicate
    data_new = data_new.loc[data_new['Same'] == False]

    # delete the 'Same' column
    cols = list(data_new.columns.values)
    data_new = data_new[cols[0:5]]

    # Fill empty Replicate cells with appropriate sample number
    data_new[['Replicate']] = data_new[['Replicate']].fillna(method='ffill')
 
    # Remove rows that only have sample name and replicates
    data_final = data_new[pd.notnull(data_new['Element'])]
    
    fileName = str(input('What would you like to name your ouput file (please include .csv)? -> '))
    # Export to csv
    data_final.to_csv(fileName, index=False)
    log_export.to_csv('logs_' + fileName, index=False)
    
data = readData()
log_export = logOutput()
cleanAndExportData()
