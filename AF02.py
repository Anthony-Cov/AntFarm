import os
import sys
import warnings

import numpy as np
import pandas as pd
import time

import matplotlib.style
import matplotlib.pyplot as plt
matplotlib.style.use('classic')
matplotlib.use('TkAgg')

import FreeSimpleGUI as sg
from FreeSimpleGUI import Text, Listbox, Checkbox, Input, Output ,Radio , Save, Submit, Image 
from FreeSimpleGUI import Button, Exit, Window, change_look_and_feel, popup_yes_no

from src.simulator import *
from src.AFLib import *
from src.environ import make_env

series=1
change_look_and_feel('SystemDefaultForReal')
#font=('Helvetica', 12)
font=('Courier', 12)
warnings.filterwarnings("ignore")
path=os.path.abspath('../src')
if path in sys.path:
    pass
else:
    sys.path.append(path)
predfile='macro_statistics.csv'
datadir='../data/processed/'

''' Здесь файлы целевых рядов и список их колонок со значениями '''


#Window layout
layout = [
    [Text('Agent-based consumption behaviour modelling.')],
    [Text('How many customers (1-5mln)?'), Input('1',key= '-NCUST-', size=(7,1)),
    Text('Period from:'),
    sg.Input('2020-01-01',key='-DFROM-', size=(10,1)), sg.CalendarButton('Date from', 
        close_when_date_chosen=True,  target='-DFROM-', format='%Y-%m-%d', default_date_m_d_y=(1,1,2020), no_titlebar=True ), 
    Text('to:'),
    sg.Input('2020-12-31',key='-DTO-', size=(10,1)), sg.CalendarButton('Date to', 
        close_when_date_chosen=True,  target='-DTO-', format='%Y-%m-%d', default_date_m_d_y=(2,1,2020)),
        Text('\t\t'), Submit(button_color='lightgreen'), Text('\t\t'), Image('Ant.png', subsample=2)], 
    [Button('Load environment', key='_LEnv_'), Button('Create environment', key='_CEnv_'), Button('Plot environment', key='_PEnv_'),Text('\t'),
     Button('Show a single customer', key='_SSC_'), Button('Plot a single customer', key='_PSC_'), 
     Button('Plot for all', key='_PALL_')], 
    [sg.ProgressBar(100, orientation='h', size=(95, 20), key='progressbar')],

    [sg.Output(size=(120, 25),  font=font,  key='-OUTPUT-')],
    [Save(),Button('Clear', key='_Clear_'), Exit(button_color='pink')] 
    ]
window = Window('Ant Farm v.0.0', layout, icon='ant.ico')
#window.layout=Output(size=(120, 30), font=font)
progress_bar = window['progressbar']
count=1
window.read(timeout=.1)
global environment
while True:                             # The Event Loop
    event, val = window.read()
    progress_bar.UpdateBar(0)
    if event in (None,'Exit'):
        break
    if event=='_CEnv_':
        environment=make_env('2020-01-01', 370)
        n=len(environment)
        print('Environment is created for dates from %s to %s'%(environment.date.min(), environment.date.max()))
        continue
    if event=='_LEnv_':
        try:
            environment=pd.read_csv('data/environment.csv', parse_dates=['date'])#.set_index('date')
            n=len(environment)
        except:
            print('File data/environment.csv doesn\'t exist or corrupted.')
        print('Environment is loaded for dates from %s to %s'%(environment.date.min(), environment.date.max()))
        continue
    if event=='_Clear_':
        window['-OUTPUT-'].Update('')
        count=1
        continue
    if event=='_PEnv_':
        if 'environment' in globals():
            environment.set_index('date').plot(figsize=(12,4))
            plt.legend(environment.columns[1:])
            plt.show()
            continue
        else:
            print('Environment is not created or loaded!')
            continue
    if event=='Save':
        t=time.localtime(time.time())
        if 'db' in globals():
            filename='sim'+str(t.tm_year)+str(t.tm_mon)+str(
                t.tm_mday)+str(t.tm_hour)+str(t.tm_min)+str(t.tm_sec)+'.csv' 
            db.to_csv(filename, index=False)
            print(filename, ' saved')
            continue
        else:
            print('No process launched, nothing to save.')
            continue
    if event=='_PSC_':
        if not ('db' in globals()):
            print('No process launched, nothing to show.')
            continue
        else:
            choice=choose_single(db)
            if choice[0]==None:
                print('Choice is not made.')
                continue
            else:
                tab=db[db.id==choice[0]][['day']+list(choice[1])]
                PlotSingle(tab)
                if choice[2]:
                    tab.to_csv(choice[0]+'.csv', index=False)
                    print(choice[0]+'.csv saved.') 
                continue
    if event=='_SSC_':
        if not ('db' in globals()):
            print('No process launched, nothing to show.')
            continue
        else:
            choice=choose_single(db)
            if choice[0]==None:
                print('Choice is not made.')
                continue
            else:
                tab=db[db.id==choice[0]][['day']+list(choice[1])]
                print('Customer %s activity'%choice[0])
                print(tab)
                if choice[2]:
                    tab.to_csv(choice[0]+'.csv', index=False)
                    print(choice[0]+'.csv saved.')  
                continue
    if event=='_PALL_':
        if not ('db' in globals()):
            print('No process launched, nothing to show.')
            continue
        else:
            choice=choose_crowd(db)
            if len(choice[1])==0:
                print('Choice is not made.')
                continue
            elif choice[0]==0:
                plot_sep(db[['day']+list(choice[1])]) 
                continue
            elif choice[0]==1:
                ams=db[['day']+list(choice[1])].groupby('day')[choice[1]].sum()
                plot_cumul(ams) 
                continue
            elif choice[0]==2:
                ams=db[['day']+list(choice[1])].groupby('day')[choice[1]].sum()
                plot_share(ams) 
                continue
            else:
                continue    
    #check data
    if val['-NCUST-'].isdecimal(): 
        ncust=int(val['-NCUST-'])
    else:
        print('Amount of customers should be a number(1-5mln)')
        continue
    if (ncust<1) | (ncust>=5000000):
        print('Amount of customers should be greater than 1 and not greater than 5mln)')
        continue   
    if not('environment' in globals()):
        print('Environment is not created or loaded!')
        continue
    dat_f, dat_s = pd.to_datetime(val['-DTO-']), pd.to_datetime(val['-DFROM-'])
    d1=(val['-DFROM-'] > val['-DTO-']) | ('' in [val['-DFROM-'] ,val['-DFROM-']])
    d2=(dat_s < environment.date.min()) | (dat_f > environment.date.max())
    if d1 | d2:
        print('Wrong dates!')
        continue
    environment.drop(environment[(environment.date<dat_s)|(environment.date>dat_f)].index, inplace=True)
    if ncust>500:
        ch = popup_yes_no("More than 500 customers! \n It may take time. \n Do you want to Continue?",  title="Really?")
        if ch=='No':
            continue
    perd=(dat_f-dat_s).days
    print('Process for %i customers from %s to %s (%i days)'%(ncust, val['-DFROM-'], val['-DTO-'], perd)) 
#    Fig='''\t   ,,,,,  \n\t Wо(0,0)о \n\t |  \~/   \n\t  \__|__  \n\t   \ : / \ \n\t   (_._)  |\n\t   | _ |  M\n\t   || || \n\t @_/   \_@ \n'''
#    print(Fig)
#    print(Fig+'Hi! I\'m a simulated consumer!')
    """Customer's properties variations in a big loop"""
    t=time.localtime(time.time())
    print('Process launched', '-'.join([str(t.tm_year),str(t.tm_mon).zfill(2),str(t.tm_mday).zfill(2)]),' ',
          ':'.join([str(t.tm_hour).zfill(2),str(t.tm_min).zfill(2),str(t.tm_sec).zfill(2)]))
    populus=[customer('Cust'+str(i).zfill(4), environment.set_index('date', drop=True)) for i in range(ncust)]
    db=pd.DataFrame(columns=['day','id','survival', 'socialization', 'self_realization'])
    for d in range(perd):
        for c in populus:
            purch=c.time_step()
            a={'day':c.day, 'id':c.id}
            #purch=market(c, c.time_step())
            a.update(purch)
            db=pd.concat([db, pd.DataFrame(a, index=[0])], ignore_index=True)
        progress_bar.UpdateBar((d+1)/perd*100)
    t=time.localtime(time.time())
    print('Process successfully finished', '-'.join([str(t.tm_year),str(t.tm_mon).zfill(2),str(t.tm_mday)]).zfill(2),' ',
          ':'.join([str(t.tm_hour).zfill(2),str(t.tm_min).zfill(2),str(t.tm_sec).zfill(2)]))
    print(db)
    print('\n')
window.close()
print('Готово')
