#Code by Darien Vazquez

import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from tkinter import filedialog
from extract import *

datapath = os.path.abspath(os.getcwd())
#print(datapath)
malwareModels = pickle.load(open(datapath+"\\pickles\\models_v2.pickle", "rb"))
print(malwareModels)
colVal = 0
listboxes = []
def filepaths(model):
    global colVal
    get_files = list(lb.get(0, tk.END))
    for filepath in get_files:
        sample, API_calls = extract(filepath, datapath)
        total = 0
        sampleRatio = 0
        if (model.get() == "Total Results") or (model.get() == "Total Percentage"):
            for key in malwareModels.keys():
                total += malwareModels[key].predict(sample)
            sampleRatio = total/4
        else:
            result = malwareModels[model.get()].predict(sample)
        listLabel = tk.LabelFrame(root, text="File: "+filepath.split('/')[-1])
        listLabel.grid(row=1, column=colVal, sticky='nsew')
        listboxes.append(listLabel)
        colVal += 1
        modelLabel = tk.Label(listLabel, text="Model used: "+model.get())
        modelLabel.grid(row=0, sticky='nsew')
        newList = tk.Listbox(listLabel)
        for call in API_calls:
            newList.insert(tk.END, call)
        newList.grid(row=1, sticky='nsew')
        if (model.get() == "Total Results"):
            if sampleRatio > 0.5:
                label = tk.Label(listLabel, text="Benign PE", bg="green")
            else:
                label = tk.Label(listLabel, text="Malware detected", bg="red")
        elif (model.get() == "Total Percentage"):
            samplePercent = sampleRatio*100
            malwarePercent = 100 - samplePercent
            label = tk.Label(listLabel, text="%d%% of models indicate file is malware"%malwarePercent)
        else:    
            if result == 0:
                label = tk.Label(listLabel, text="Malware detected", bg="red")
            else:
                label = tk.Label(listLabel, text="Benign PE", bg="green")
        label.grid(row=2, sticky='nsew')



def openExplore(listbox):
    folder_path = filedialog.askopenfilename()
    listbox.insert('end', folder_path)

def clearFiles(listbox):
    size = listbox.size()
    for i in range(size):
        listbox.delete(i)
    for i in listboxes:
        i.destroy()


root = TkinterDnD.Tk()
#root.geometry("1000x500")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame = tk.Frame(root)
#frame.pack()
frame.grid()
root.title('Malware Detection')

#title = tk.Label(root, text="Malware Detection", height=5, font=('Times New Roman', 15, 'bold'))
#title.pack(side=tk.TOP)
#title.grid(row=0)
#title.grid_rowconfigure(0, weight=1)
#title.grid_columnconfigure(0, weight=1)
#title.grid_columnconfigure(0, weight=0)

listTitle = tk.LabelFrame(root, text="Please place files here")
#listTitle.pack(fill='both', side=tk.LEFT, padx=15, pady=15)
listTitle.grid(row=1, column=colVal, sticky='nsew')
colVal+=1
lb = tk.Listbox(listTitle)

lb.drop_target_register(DND_FILES)
lb.dnd_bind('<<Drop>>', lambda e: lb.insert(tk.END, str(e.data[1:-1])))
#listTitle.pack()
#lb.pack(side=tk.LEFT)
lb.grid(row=0, sticky='nsew')

browse_button = tk.Button(listTitle, text="Browse Files", width=25, command=lambda: openExplore(lb))
#browse_button.pack(side=tk.BOTTOM)
browse_button.grid(row=1, sticky='nsew')

options = ['Total Results', 'Total Percentage', 'Logistic Regression', 'SVM', 'Decision Tree', 'Random Forest']
clicked = tk.StringVar()
clicked.set(options[0])
drop = tk.OptionMenu(listTitle, clicked, *options)
drop.grid(row=2, sticky='nsew')


submit_button = tk.Button(listTitle, text='Process Files', width=25, command=lambda: filepaths(clicked))
#submit_button.pack()
submit_button.grid(row=3, sticky='nsew')
clear_button = tk.Button(listTitle, text="Clear all files", width=25, command=lambda: clearFiles(lb))
clear_button.grid(row=4, sticky='nsew')

root.mainloop()