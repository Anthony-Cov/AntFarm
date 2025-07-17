import numpy as np
import pandas as pd
import matplotlib.style
import matplotlib.pyplot as plt
matplotlib.style.use('classic')
matplotlib.use('TkAgg')

from FreeSimpleGUI import Text,Checkbox, Submit, Input, Button, Radio, popup
from FreeSimpleGUI import Exit, Window



def PlotSingle(tab):
    s=tab[tab.columns[1:]].sum().sum()
    plt.figure(figsize=(12,9))
    plt.plot(tab.set_index('day', drop=True).astype(float).fillna(0), marker='o')
    plt.title('Expenses for %.2f thousand per %i days'%(s/1000, len(tab)), size=20)
    plt.xticks(size=14, rotation=60)
    plt.yticks(size=14)
    plt.xlabel('DATE', size=16)
    plt.ylabel('PAYMENT', size=16)
    plt.grid()
    plt.legend(tab.columns[1:], fontsize=14)
    plt.tight_layout()
    plt.show()
    return()
 
def choose_single(db):
    choice=['survival','socialization','self_realization']
    layout = [
        [Text('\tMake your choice')],
        [Text('Customer\'s number'), Input('0',key= '-CID-', size=(7,1))],
        [Text('\tWhich of categories?')],
        [[Checkbox(i,True)] for i in choice],#5
        [Checkbox('Save table',False, key='-STab-')],
        [Submit(), Button('Clear all', key='_Clear_'), Exit()] 
    ]
    window = Window('Choice for a customer', layout)
    window.read(timeout=.1)
    while True:
        event, val = window.read()
        if event in (None,'Exit'):
            cid=None
            choice=np.array([])
            break
        if event=='_Clear_':
            for i in range(db.category.nunique()):
                window[i](False)
        else: 
            if val['-CID-'].isdecimal(): 
                cid='Cust'+val['-CID-'].zfill(4)
                if not (cid in db.id.unique()):
                    popup('No %s among customers! Number < %i'%(cid,db.id.nunique()))
                    continue
                elif sum(list(val.values())[1:])<1:
                    popup('At least one category should be chosen')
                    continue
                else:
                    choice=np.array(choice)[list(val.values())[1:-1]]
                    break
            else:
                popup('Amount of customers should be a number(1-5mln)')
            continue
    window.close()
    return (cid, choice, val['-STab-'])

def choose_crowd(db):
    choice=['survival','socialization','self_realization']
    layout = [
        [Text('\tMake your choice')],
        [Text('What kind of plot?')],
             [Radio('Separate series', "RADIO1", default=True)],#0
             [Radio('Cumulative series', "RADIO1", default=False)],
             [Radio('Shares of groups', "RADIO1", default=False)],
        [Text('\tWhich of categories?')],
        [[Checkbox(i,True)] for i in choice],#5
        [Submit(), Button('Clear all', key='_Clear_'), Exit()] 
    ]
    window = Window('Choice for the crowd', layout, icon='bspb-ru.ico')
    window.read(timeout=.1)
    while True:
        event, val = window.read()
        if event in (None,'Exit'):
            choice=np.array([])
            kind=None
            break
        if event=='_Clear_':
            for i in range(db.category.nunique()):
                window[i+3](False)
        else: 
            if sum(list(val.values())[3:])<1:
                popup('At least one category should be chosen')
                continue
            else:
                choice=np.array(choice)[list(val.values())[3:]]
                kind=list(val.values())[0:3].index(True)
                break
            continue
    window.close()
    return (kind, choice)

def plot_sep(data):        
    c=data.columns[1:]
    d=data.groupby('day')[c].sum().fillna(value=0.)
    d.fillna(0).plot(figsize=(12,5),grid=True, xlabel='Date', ylabel='Payment')
    plt.legend([i.capitalize() for i in c])
    plt.tight_layout()
    plt.show()
    return None

def plot_cumul(ams):
    colors=['tab:blue','tab:orange','tab:green']
    scale=ams.sum(axis=1).max()
    plt.figure(figsize=(18,13))
    plt.title('Expenses', size=20)
    ser=np.zeros(len(ams))
    for i,c in zip(ams.columns, colors):
        s1=ser.copy()
        ser+=ams[i].values/scale
        plt.plot(ser)
        plt.fill_between(np.arange(len(ser)), s1, ser, color=c, alpha=.5, label=i.replace('_','-').capitalize())
    xt=np.arange(0, len(ams)+1, 14)
    plt.xticks(xt, ams.index.strftime('%Y-%m-%d').values[xt], size=14, rotation=30)
    plt.yticks(size=14)
    plt.xlabel('DATE', size=16)
    plt.ylabel('Normalized PAY_AMOUNT', size=16)
    plt.legend(fontsize=14)
    plt.grid(axis='both')
    plt.tight_layout()
    plt.show()
    return None  

def plot_share(ams):
    colors=['tab:blue','tab:orange','tab:green']
    plt.figure(figsize=(18,13))
    plt.title('Relative expenses', size=20)
    s={}
    for i in ams.columns: # 6536,
        s[i]=[]
        for j in ams.index:
            scale=ams.sum(axis=1)
            s[i].append(ams.loc[j][i]/scale[j])
    ser=np.zeros(len(ams))
    for i,c in zip(ams.columns, colors):
        s1=ser.copy()
        ser+=s[i] #Norm01(ams[i].values)[0]
        plt.plot(ser)
        plt.fill_between(np.arange(len(ser)), s1, ser, color=c, alpha=.5, label=i.replace('_','-').capitalize())
    xt=np.arange(0, len(ams)+1,14)
    plt.xticks(xt, ams.index.strftime('%Y-%m-%d').values[xt], size=14, rotation=30)
    plt.yticks(size=14)
    plt.xlabel('DATE', size=16)
    plt.ylabel('RELATIVE PAY_AMOUNT', size=16)
    plt.legend(fontsize=14)
    plt.grid(axis='both')
    plt.tight_layout()
    plt.show()
    return None   
#                                  
    
