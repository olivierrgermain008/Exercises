import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import showinfo
from tkinter import font
import pandas as pd
import time
from PIL import Image, ImageTk
import io
from urllib.request import urlopen
import winsound
from functools import partial
import numpy as np
from numpy import random
import warnings

warnings.filterwarnings('ignore')

"""
Backlog items:
    Add a menu for file loading, user config and help
    Better countdown sounds
    Use different sets, including rep based
    Record results
    Read config from JSON
    Play music during exercise
        Longer-term:
            Publish on GitHub
            Make it a web-based application
            Try .NetCore...
"""

"""
Credits
    Basic reference information about tkinter was found at:
        https://pythonistaplanet.com/how-to-create-a-desktop-application-using-python/
    Create a menu bar:
        https://www.pythontutorial.net/tkinter/tkinter-menu/
    Scrollbar method from:
        https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter

"""

app_version_number = '1.0.0.'

# create initial root windows properties
root = tk.Tk()
root.title("Exercise series")
root.geometry("395x760+2121+150")
root.configure(bg='grey')
root.iconbitmap('Fit_icon.ico')
root.minsize(200,100)

# function to pop out the application version
def about_app():
    showinfo(title = 'About this app', message = f'This is version {app_version_number} of the Exercise Application')

# function to pop out the copyright
def message_copyright():
    showinfo(message = 'Copyright 2022, Olivier Germain, All rights reserved')

# create the menu bar on the root window
menubar = tk.Menu(root)
root.config(menu=menubar)
file_menu = tk.Menu(
    menubar,
    tearoff=0
)

# add Exit menu item
file_menu.add_command(
    label='Exit',
    command=root.destroy
)

# add the File menu to the menubar
menubar.add_cascade(
    label="File",
    menu=file_menu
)
# create the Help menu
help_menu = tk.Menu(
    menubar,
    tearoff=0
)

help_menu.add_command(
    label='About...',
    command = about_app
    )

help_menu.add_command(
    label = 'Copyright',
    command = message_copyright
    )

# add the Help menu to the menubar
menubar.add_cascade(
    label="Help",
    menu=help_menu
)

# read excel, extracts the unique types of exercises
exodatasheet = pd.read_excel("Exercises.xlsx")
exo_type_list = exodatasheet['Type'].unique()
# Creates a dictionary object to be able to select which exercise type is of interest
selected = [tk.StringVar(value ='1') for ex in exo_type_list] # with value = 1, all check boxes will be pre-ticked
exo_select = {ex : '1' for ex in exo_type_list} # and the preset value is also in the dico

# Create checkbox class
class exo_checkbox():
    # This class sets the baseline characteristics for each checkbox based on the name and index from external inputs
    def __init__(self, parent, name, index):
        self.parent  = parent
        self.name = name
        self.label = tk.Checkbutton(
            parent, 
            text = name, 
            command=partial(choose, index),
            variable = selected[index],
            onvalue ='1',
            offvalue = '0'
            )
    # Place button - pack can be called as a method of that class
    def pack(self, **kwargs):
        self.label.pack(kwargs)

# Action for the checkbox class
def choose(number):
    check_result = selected[int(number)].get()
    exo_select[exo_type_list[number]]=check_result
    
# get exercise and picture
def result(next):
    exercise_name = exodatasheet['Exercise'][next]
    exercise_url = exodatasheet['Picture'][next]
    return (exercise_name, exercise_url)

#function to protect against accidental closing a window
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
       root.destroy()
    else:
        pass

# protect root window closure 
root.protocol("WM_DELETE_WINDOW", on_closing)

# function to start main track when user presses Enter
def process(event):
    config_countdown()

# Set exercises parameters by reading values from the initial window
def config_countdown():
    # get difficulty input by user from radio buttons
    valuedif = selected_dif.get()
    countdown_time = int(valuedif)
    global pause_ready
    global pause_set
    global beep
    beep = 1
    if countdown_time ==0:
        pause_ready = 1
        pause_set = 1
        beep = 0
    elif countdown_time < 61:
        pause_ready = 5
        pause_set = 3
    else:
        pause_ready = 10
        pause_set = 8
   
    # set up exercises list

    # run_exo will be the dictionary that will hold the list of selected types of exercises paired with the index in order or not
    exo_selected = [k for (k,v) in exo_select.items() if v =='1']
    if exo_selected ==[]:
        messagebox.showerror("Warning", "You must select at least one exercise type")
        root.mainloop()   
    run_exo ={}
    for exo in exo_selected:
        list_of_items = []
        for item in range(len(exodatasheet)):
            if exodatasheet['Type'][item] == exo:
                list_of_items.append(item)
        run_exo[exo] = list_of_items
    selrand = selected_rand.get()
    if selrand == '1':
        for exo in exo_selected:
            np.random.shuffle(run_exo[exo])

    # set app windows size
    screen_width = int(root.winfo_screenwidth()*0.9)
    screen_height = int(root.winfo_screenheight()*0.9)
    exogeometry = str(screen_width)+"x"+str(screen_height)+"+"+str(root.winfo_screenwidth()+5)+"+5"
    
    # compute number of exercises
    total_exo = 0
    for item in run_exo.keys():
        total_exo += len(run_exo[item])
    
    # compute ordered list of exercises
    exo_indexed_for_run = []
    item = 0
    rank = 0
    while item < total_exo:
        for ex in run_exo.keys():
            if rank < len(run_exo[ex]):
                exo_indexed_for_run.append(run_exo[ex][rank])
                item +=1
        rank +=1
    
    # get answer from combo boxes
    if selected_duration.get() == '' and selected_number_of_exos.get() == '':
        messagebox.showerror('Error', 'You must select at least one option.')
        root.mainloop()
    elif selected_duration.get() != '' and selected_number_of_exos.get() != '':
        messagebox.showerror('Error', 'You can select only one option.')
        root.mainloop()
    elif selected_duration.get() != '':
        # compute number of exercises for duration choice
        my_selected_duration = np.round(int(selected_duration.get())*60,0)
        number_exo = int(my_selected_duration/(pause_ready+pause_set+countdown_time))
    else:
    # compute number of exercises for fixed number choice
        number_exo_res = selected_number_of_exos.get()
        if number_exo_res[0:3] == 'All':
            number_exo = len(exo_indexed_for_run)
        elif number_exo_res[0:3] == 'Hal':
            number_exo = int(len(exo_indexed_for_run)/2)
        elif number_exo_res[0:3] == 'One':
            number_exo = int(len(exo_indexed_for_run)*1.5)
        elif number_exo_res[0:3] == 'Twi':
            number_exo = len(exo_indexed_for_run)*2
        else:
            number_exo = int(number_exo_res)  
    # compute exercise list for duration or number of exercises
    while number_exo > len(exo_indexed_for_run):
        exo_indexed_for_run.extend(exo_indexed_for_run)
    exo_indexed_for_run = exo_indexed_for_run[0:number_exo]

# clean root window for the exercises and resize
    subttl1.destroy()
    vertical_scrollbar_root.destroy()
    popcanvas.destroy()
    root.geometry(exogeometry)

# Countdown
    # Run each exercise
    for exo in exo_indexed_for_run:
        # create and place photo of the next exercise
        address = result(exo)[1]
        if str(address)[0:4] == "http":
        # open the web page picture and read it into a memory stream and convert to an image Tkinter can handle
            my_webimage = urlopen(result(exo)[1])
            # create an image file object
            my_picture = io.BytesIO(my_webimage.read())
        else:
            my_picture = address
        # use PIL to open image formats like .jpg  .png  .gif  etc.
        pil_img = Image.open(my_picture)
        imagebg = ImageTk.PhotoImage(pil_img)
        img_height = int(screen_height * 0.9)
        img_width = int(imagebg.width() / int(imagebg.height()) * img_height)
        if img_width > screen_width*0.9:
            img_width = int(screen_width * 0.9)
            img_height = int(imagebg.height() / imagebg.width() * img_width)
        resized_image= pil_img.resize((img_width,img_height), resample = Image.ANTIALIAS)
        imagebg = ImageTk.PhotoImage(resized_image)
        label1 = ttk.Label(root, image=imagebg)
        label1.place(relx = 0.05, rely = 0.05, anchor= 'nw')
        exercise_name_display = ttk.Label(root, text = result(exo)[0], font = ("Arial", 80), background = "grey")
        exercise_name_display.place (relx = 0.9, rely = 0.02, anchor = 'ne')
        root.update()
        # create and place "ready, set, go" countdown
        count_display = ttk.Label(root, text = "Ready...", font = ("Arial", 100), background = "grey")
        count_display.place(relx = 0.75, rely = 0.25, anchor = 'nw')
        winsound.Beep(500, 500*beep)
        root.update()
        time.sleep(pause_ready)
        count_display.destroy()
        count_display = ttk.Label(root, text = "Set...", font = ("Arial", 100), background = "grey")
        count_display.place(relx = 0.75, rely = 0.25, anchor = 'nw')
        winsound.Beep(1000, 500*beep)
        root.update()
        time.sleep(pause_set)
        count_display.destroy()
        count_display = ttk.Label(root, text = "Go!", font = ("Arial", 100), background = "grey", foreground= "red")
        count_display.place(relx = 0.75, rely = 0.25, anchor = 'nw')
        winsound.Beep(1500, 500*beep)
        root.update()
        time.sleep(1)
        count_display.destroy()
        root.update()
        # run countdown of exercise
        exercise_duration = countdown_time
        while exercise_duration:
            sec_count_display = ttk.Label(root, text = str(exercise_duration-1) + " s", font = ("Arial", 200), background = "grey")
            sec_count_display.place(relx = 0.65, rely = 0.25, anchor = 'nw')
            root.update()
            exercise_duration -=1
            time.sleep(1)
            sec_count_display.destroy()
        label1.destroy()
        exercise_name_display.destroy()
    #end of count
    root.destroy()
    messagebox.showinfo("Time is up", "Enough for today")

# Main track - running the root.mainloop

# Populate 'root' window with multiple selections and validate button
#
# Create selector for exercise types
subttl1 = tk.Label(root, text = 'Your choices for today', bg = 'grey', font = ('Arial', 16), fg = 'white')
subttl1.pack(fill ='x', padx = 5, pady =5)
f = font.Font(subttl1, subttl1.cget("font"))
f.configure(underline=True, weight ='bold')
subttl1.configure(font=f)
popcanvas = tk.Canvas(root)
global_frame = ttk.Frame(popcanvas)
# global_frame.pack()
vertical_scrollbar_root = ttk.Scrollbar(root, orient='vertical', command=popcanvas.yview)
popcanvas.configure(yscrollcommand = vertical_scrollbar_root.set)
vertical_scrollbar_root.pack(side = 'right', fill ='y')
popcanvas.pack(side='left', fill='both', expand =True)
popcanvas.create_window((0,0), window=global_frame, anchor="nw")
global_frame.bind("<Configure>", lambda event, canvas=popcanvas: onFrameConfigure(popcanvas))

# Reset the scroll region to encompass the inner frame
def onFrameConfigure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

subttl2 = tk.Label(global_frame, text = 'Select targets of exercises', fg = 'white', bg = 'grey', font = ('Arial', 12))
subttl2.pack(fill ='x', padx = 5, pady =5)

sel_ex_frame = tk.Frame(global_frame)
sel_ex_frame.pack()
ind = tk.IntVar
ind = 0
for exo in exo_type_list:
    sectionHeader = exo_checkbox(sel_ex_frame, exo, ind)
    sectionHeader.pack(fill ='x', padx = 5, pady =5)
    ind += 1

# create Radio buttons to pick-up difficulty of exercise
subttl3 = tk.Label(global_frame, text = 'Select difficulty', fg = 'white', bg = 'grey', font = ('Arial', 12))
subttl3.pack(fill ='x', padx = 5, pady =5)
select_dif_frame = tk.Frame(global_frame)
select_dif_frame.pack()
selected_dif = tk.StringVar()
selected_dif.set(30) # this pre-selects difficulty to Normal
difficulty = {'Really hard': 60, 'Hard': 45, 'Normal': 30, 'Easy': 20, 'Beginner': 15, 'Test' : 0}

for dif in difficulty:
    r = tk.Radiobutton(
        select_dif_frame,
        text=dif,
        value=difficulty[dif],
        variable=selected_dif
    )
    r.pack(fill='x', padx=5, pady=5)

# create Radio buttons to select Randomized order or not
subttl4 = tk.Label(global_frame, text = 'Random or ordered?', fg= 'white', bg = 'grey', font = ('Arial', 12))
subttl4.pack(fill ='x', padx = 5, pady =5)
select_rand_frame = tk.Frame(global_frame)
select_rand_frame.pack()
selected_rand = tk.StringVar()
selected_rand.set(False) # this presets the answer as being Ordered
randororder = {'Random': True, 'Ordered': False}

for choice in randororder:
    rdiff = tk.Radiobutton(
        select_rand_frame,
        text=choice,
        value=randororder[choice],
        variable=selected_rand
    )
    rdiff.pack(fill='x', padx=5, pady=5)

# Create 2 ComboBoxes to enter desired duration or number of exercises
subttl5 = tk.Label(global_frame, text = 'How long do you want to exercise (in mins)?', fg= 'white', bg = 'grey', font = ('Arial', 12))
subttl5.pack(fill ='x', padx = 5, pady =5)
selected_duration = tk.StringVar()
duration_cb = ttk.Combobox(global_frame, textvariable=selected_duration)
duration_cb['values'] = [5, 10, 15, 20, 25, 30]
duration_cb.pack()
subttl6 = tk.Label(global_frame, text = 'Or enter how many exercises you want to go through?', fg= 'white', bg = 'grey', font = ('Arial', 12))
subttl6.pack(fill ='x', padx = 5, pady =5)
selected_number_of_exos = tk.StringVar()
numb_exerc_cb = ttk.Combobox(global_frame, textvariable=selected_number_of_exos)
total_possible = str(len(exodatasheet))
half_possible = str(int(len(exodatasheet)/2))
one_anda_half_possible = str(int(len(exodatasheet)*1.5))
twice_possible = str(len(exodatasheet)*2)
numb_exerc_cb['values'] = [
    f'All (~{total_possible})', 
    f'Half (~{half_possible})', 
    f'One and a half (~{one_anda_half_possible})',
    f'Double (~{twice_possible})'
    ]
numb_exerc_cb.pack()

button = tk.Button(
    global_frame,
    text="Validate",
    command= config_countdown
)
button.pack(padx=5, pady=5, ipadx=5, ipady=5)
button.focus()
root.bind('<Return>', process)

root.mainloop()