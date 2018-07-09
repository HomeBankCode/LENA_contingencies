"""
The MIT License (MIT)
Copyright (c) 2018 Paul Yoder et al.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

This module is the main UI of the application as well as the main thread.
"""

import ttk, tkFileDialog
from Tkinter import *
from Batch import Batch
from SeqAnalysis2 import SeqAnalysis
import os
import platform
import threading
import time
import ast
import tkMessageBox
from Helpers import *
import xml.etree.ElementTree as ET
import csv

MAC = 'Darwin'
WINDOWS = 'Windows'
LINUX = 'Linux'
AB = 'A_B'
ABC = 'AB_C'
ABC2 = 'A_BC'
OK = 'ok'
MAXTHREADS = 4
codes = ['MAN','MAF','FAN','FAF','CHNSP','CHNNSP', \
			'CHF','CXN','CXF','NON','NOF','OLN','OLF','TVN', \
			'TVF','SIL']
code_use = {'MAN':False,'MAF':False,'FAN':False,'FAF':False,'CHNSP':False,'CHNNSP':False, \
			'CHF':False,'CXN':False,'CXF':False,'NON':False,'NOF':False,'OLN':False,'OLF':False,'TVN':False, \
			'TVF':False,'SIL':False}
codes_index = {'MAN':0,'MAF':1,'FAN':2,'FAF':3,'CHNSP':4,'CHNNSP':5, \
			'CHF':6,'CXN':7,'CXF':8,'NON':9,'NOF':10,'OLN':11,'OLF':12,'TVN':13, \
			'TVF':14,'SIL':15}

class LenaUI:
    """This class is the UI and associated actions"""
    def __init__(self, root):
        """
        UI started on init of class
        :param root:
        """
        self.root = root
        root.resizable(False, False)
        root.title("LENA Contingencies")

        # Class Attributes
        self.file_dict = {} # k:ID v:path/to/file
        self.csv_file_dict = {} # k:ID v:path/to/file
        self.input_dir = StringVar()
        self.output_dir = StringVar()
        self.output_format = []
        self.seq_config = {}
        self.pause_duration = DoubleVar()
        self.pause_duration.set(0.1)
        self.minutes_of_pause_to_keep = DoubleVar()
        self.minutes_of_pause_to_keep.set(0.0)
        self.rounding_enabled = BooleanVar()
        self.keep_pauses = BooleanVar()
        self.sequence_type = StringVar()
        self.var_a = []
        self.var_b = []
        self.var_c = []
        self.output_format.append(".csv") # set to csv default
        self.output_msg = ""
        self.output_msg_counter = 0
        self.num_threads = IntVar()
        self.num_threads.set(4)
        self.start_time = None
        self.seq_run_results = []

        # Create main frames
        main_frame = ttk.Frame(self.root) # top, mid, btm frames embedded within this frame
        self.top_frame = ttk.Frame(main_frame, borderwidth=5, relief="sunken", width=200, height=150)
        self.mid_frame = ttk.Frame(main_frame, borderwidth=5, relief="sunken", width=200, height=300)
        self.btm_frame = ttk.Frame(main_frame, borderwidth=5, relief="sunken", width=200, height=100)

        # create menu
        menubar = Menu(root) # create menu bar
        root.config(menu=menubar) # attach menubar to root window

        # file menu
        file_menu = Menu(menubar) # create "File" menu item     
        file_menu.add_command(label="Instructions", command=self.load_instruction_window) # add a command to "Help" menu item
        file_menu.add_command(label="Change Thread Count", command=self.change_threads_window)
        file_menu.add_command(label="Exit", command=self.close_program) # add a command to "File" menu item    
        menubar.add_cascade(label="File", menu=file_menu)   # attach "File" menu item to menubar

        # setup main frames to grid
        # top, mid, btm frames laid out inside main_frame
        # sticky tags used to keep UI elements together when stretched
        main_frame.grid(row=0, column=0) 
        self.top_frame.grid(row=0, column=0, sticky=W+E+S+N)
        self.mid_frame.grid(row=1, column=0, sticky=W+E+S+N)
        self.btm_frame.grid(row=2, column=0, sticky=W+E+S+N)

        # Setup Individual Frames
        self.setup_top_frame()
        self.setup_mid_frame()
        self.setup_btm_frame()

        # OSX ONLY - bring window to front
        if platform.system() == MAC:
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

    def change_threads_window(self):
        """
        Window for changing the number of threads used by SequenceAnalysis
        :return:
        """
        # setup
        t = Toplevel(self.root)
        t.resizable(False, False)

        # create widgets
        top_frame = Frame(t, width=100, height=50)
        t.wm_title("Set Threads")
        l = Label(t, text="Set number of threads to use\nwhen performing analysis: \n(default=4)")
        s = Spinbox(t, from_=4, to=50, textvariable=self.num_threads, width=4)
        b = ttk.Button(t, text="close", command=lambda: t.destroy(), width=4)

        # arrange widgets
        l.grid(row=0, column=0, padx=5, pady=7)
        s.grid(row=1, column=0, sticky=W, padx=15, pady=5)
        b.grid(row=1,column=0, sticky=E, padx=15, pady=5)

    def change_pause_duration_up(self, event):
        """
        Updates(+.01) pause duration variable. Bound to mid_pause_up_btn.
        :param event:
        :return:
        """
        if self.pause_duration.get() < 10.0:
            self.pause_duration.set(round(self.pause_duration.get()+0.1,1))

    def change_pause_duration_down(self, event):
        """
        Updates(-.01) pause duration variable. Bound to mid_pause_dn_btn.
        :param event:
        :return:
        """
        if self.pause_duration.get() >= 0.1:
            self.pause_duration.set(round(self.pause_duration.get()-0.1,1))

    def change_pause_duration_slider(self,event):
        """
        Updates pause duration variable. Bound to mid_pause_slider.
        :param event:
        :return:
        """
        self.pause_duration.set(round(self.pause_duration.get(),1))

    ## Pause Removal
    def change_pause_to_keep_duration_up(self, event):
        """"Updates(+.01) pause duration variable. Bound to mid_pause_up_btn."""
        if self.minutes_of_pause_to_keep.get() < 10.0:
            self.minutes_of_pause_to_keep.set(round(self.minutes_of_pause_to_keep.get()+0.1,1))

    def change_pause_to_keep_duration_down(self, event):
        """"Updates(-.01) pause duration variable. Bound to mid_pause_dn_btn."""
        if self.minutes_of_pause_to_keep.get() >= 0.0:
            self.minutes_of_pause_to_keep.set(round(self.minutes_of_pause_to_keep.get()-0.1,1))

    def change_pause_to_keep_duration_slider(self,event):
        """"Updates pause duration variable. Bound to mid_pause_slider."""
        self.minutes_of_pause_to_keep.set(round(self.minutes_of_pause_to_keep.get(),1))

    def setup_top_frame(self):
        """
        Configure top frame. Includes save, load, reset, input, output, and output selection(txt/csv/xlsx).
        :return:
        """
        # TOP FRAME CONFIG
        # Create top frame widgets
        self.csv_var = BooleanVar() # holds user selection for csv output
        self.txt_var = BooleanVar() # holds user selection for txt output
        self.xl_var = BooleanVar()  # holds user selection for xlsx output

        top_dir_label = ttk.Label(self.top_frame, text="Specify Directory")
        top_reset_btn = ttk.Button(self.top_frame, text="RESET", command=self.reset_config)
        top_load_btn = ttk.Button(self.top_frame, text="LOAD", command=self.load_config)
        top_save_btn = ttk.Button(self.top_frame, text="SAVE", command=self.save_config)
        top_input_label = ttk.Label(self.top_frame, text="Input:")
        top_output_label = ttk.Label(self.top_frame, text="Output:")
        top_format_label = ttk.Label(self.top_frame, text="Output Format")        
        self.top_csv_btn = ttk.Checkbutton(self.top_frame, text='.csv', command=self.set_output_var, variable=self.csv_var,onvalue=1, offvalue=0)
        self.csv_var.set(1) # set to csv default
        self.top_txt_btn = ttk.Checkbutton(self.top_frame, text=".txt", command=self.set_output_var, variable=self.txt_var,onvalue=1, offvalue=0)
        self.top_xl_btn = ttk.Checkbutton(self.top_frame, text=".xlsx", command=self.set_output_var, variable=self.xl_var,onvalue=1, offvalue=0)
        top_filler = ttk.Label(self.top_frame, text="      ")
        top_in_browse_btn = ttk.Button(self.top_frame, text="Browse...", command=self.select_input_dir)    #Browse button for input directory //J
        top_out_browse_btn = ttk.Button(self.top_frame, text="Browse...", command=self.select_output_dir)   #Browse button for output directory //J
        self.top_in_path = Entry(self.top_frame, width=20, textvariable=self.input_dir, state=DISABLED)     #create the label to display input directory path //J      
        self.top_out_path = Entry(self.top_frame, width=20, textvariable=self.output_dir, state=DISABLED)   #create the label to display output directory path //J
        
        # setup top frame widgets
        top_reset_btn.grid(row=0, column=3, sticky=E)
        top_dir_label.grid(row=1, column=0, columnspan=2, sticky=N)
        top_input_label.grid(row=2, column=0, sticky=E)
        top_output_label.grid(row=3, column=0, sticky=E)
        top_in_browse_btn.grid(row=2, column=3) #
        top_out_browse_btn.grid(row=3, column=3)#
        self.top_in_path.grid(row=2, column=1, columnspan=2) #
        self.top_out_path.grid(row=3, column=1, columnspan=2)#
        
        top_format_label.grid(row=5, column=0, columnspan=2)
        top_filler.grid(row=4, column=0)
        self.top_csv_btn.grid(row=6, column=0)
        self.top_txt_btn.grid(row=6, column=1)
        self.top_xl_btn.grid(row=6, column=2)
        top_load_btn.grid(row=0, column=2)
        top_save_btn.grid(row=0, column=1)

    def change_abc_var(self, event):
        """
        Updates var_a, var_b, or var_c. Bound to mid_abc_a_box, mid_abc_b_box, and mid_abc_a_box.
        :param event:
        :return:
        """
        # get user selection; id -> value
        selection = event.widget.curselection()
        templist = []
        for sel in selection:
            templist.append(event.widget.get(sel))

        # assign to appropriate var_
        if (event.widget == self.mid_abc_a_box):
            self.var_a = templist
            print("A: "+str(self.var_a))
        elif (event.widget == self.mid_abc_b_box):
            self.var_b = templist
            print("B: "+str(self.var_b))
        elif (event.widget == self.mid_abc_c_box):
            self.var_c = templist
            print("C: "+str(self.var_c))

    def get_labels(self):
        """
        Parses the .its/.csv files for the event type labels to populate the UI for sequence analysis selection.
        :return:
        """
        labels = set()

        #Loop through files in directory
        for filename in self.file_dict:

            #catch for .its files
            if self.file_dict[filename].endswith('.its'):
                tree = ET.parse(self.file_dict[filename])
                root = tree.getroot()

                #Loop through segments in file
                for segment in root.iter('Segment'):
                    if segment.get('spkr') != None:
                        if segment.get('spkr') == 'CHN':
                            if segment.get('startUtt1') != None:
                                labels.add('CHNSP')
                            else:
                                labels.add('CHNNSP')
                        else:
                            labels.add(segment.get('spkr'))

            elif self.file_dict[filename].endswith('.csv'):
                with open(self.file_dict[filename]) as csvFile:
                    reader = csv.DictReader(csvFile)
                    for row in reader:
                        if row['ID'] not in codes:
                            codes.append(row['ID'])
                            code_use[row['ID']] = False
                            codes_index[row['ID']] = len(codes)-1
                        labels.add(row['ID'])
                csvFile.close()

            else: continue

        #print labels
        for tag in labels:
            code_use[tag] = True;

        self.setup_mid_frame()




    def setup_mid_frame(self):
        """
        Configure mid frame. Includes sequence type selection and variable selection(a,b,c).
        :return:
        """
        # MID FRAME CONFIG
        # create mid frame
        used_codes = ()
        for code in codes:
            if code_use[code]:
                used_codes += (code,)
        code_vars = StringVar(value=used_codes)


        self.mid_abc_a_box = Listbox(self.mid_frame, height=8, listvariable=code_vars, selectmode=MULTIPLE, width=9, exportselection=False)
        self.mid_abc_b_box = Listbox(self.mid_frame, height=8, listvariable=code_vars, selectmode=MULTIPLE, width=9, exportselection=False)
        self.mid_abc_c_box = Listbox(self.mid_frame, height=8, listvariable=code_vars, selectmode=MULTIPLE, width=9, exportselection=False)
        
        self.mid_abc_a_box.bind("<<ListboxSelect>>", self.change_abc_var)
        self.mid_abc_b_box.bind("<<ListboxSelect>>", self.change_abc_var)
        self.mid_abc_c_box.bind("<<ListboxSelect>>", self.change_abc_var)

        def disable_c():
            self.mid_abc_c_box.configure(state="disable")
            self.mid_abc_c_box.update()

        def enable_c():
            self.mid_abc_c_box.configure(state="normal")
            self.mid_abc_c_box.update()

        mid_type_label = ttk.Label(self.mid_frame, text='Type of Analysis')       
        self.mid_ab_btn = ttk.Radiobutton(self.mid_frame, text='A ---> B', variable=self.sequence_type, value=AB, command=disable_c)
        self.mid_abc_btn = ttk.Radiobutton(self.mid_frame, text='( A ---> B ) ---> C', variable=self.sequence_type, value=ABC, command=enable_c)        
        #Added for FR-17. Changes oder of operations from (A->B)->C to A->(B->C)
        self.mid_abc2_btn = ttk.Radiobutton(self.mid_frame, text='A ---> ( B ---> C )', variable=self.sequence_type, value=ABC2, command=enable_c)

        mid_filler_label = ttk.Label(self.mid_frame, text="     ")
        mid_conf_label = ttk.Label(self.mid_frame, text="Configure Analysis")
        mid_conf_abc_a_label = ttk.Label(self.mid_frame, text="A") 
        mid_conf_abc_b_label = ttk.Label(self.mid_frame, text="B") 
        mid_conf_abc_c_label = ttk.Label(self.mid_frame, text="C") 
 
        mid_filler_label2 = ttk.Label(self.mid_frame, text="     ")
        mid_pause_label = ttk.Label(self.mid_frame, text="Pause Duration  (seconds)")
        mid_filler_label3 = ttk.Label(self.mid_frame, text="     ")
        self.mid_pause_slider = ttk.Scale(self.mid_frame, orient=HORIZONTAL, length=100, from_=0.1, to=10.0, variable=self.pause_duration,command=lambda r: self.change_pause_duration_slider(self))
        mid_pause_dn_btn = ttk.Button(self.mid_frame, text="<", command=lambda: self.change_pause_duration_down(self), width=1)
        mid_pause_up_btn = ttk.Button(self.mid_frame, text=">", command=lambda: self.change_pause_duration_up(self), width=1)
        self.mid_pause_entry = ttk.Entry(self.mid_frame, textvariable=self.pause_duration, width=4)
        self.mid_pause_checkbox = ttk.Checkbutton(self.mid_frame, text="Enable rounding", variable=self.rounding_enabled,onvalue=True, offvalue=False)
        self.mid_keep_pause_checkbox = ttk.Checkbutton(self.mid_frame, text="Keep All Pauses", variable=self.keep_pauses,onvalue=True, offvalue=False)

        mid_pause_to_keep_label = ttk.Label(self.mid_frame, text="Pauses To Keep (minutes)")
        self.mid_pause_to_keep_slider = ttk.Scale(self.mid_frame, orient=HORIZONTAL, length=100, from_=1, to=360, variable=self.minutes_of_pause_to_keep,command=lambda r: self.change_pause_to_keep_duration_slider(self))
        mid_pause_to_keep_dn_btn = ttk.Button(self.mid_frame, text="<", command=lambda: self.change_pause_to_keep_duration_down(self), width=1)
        mid_pause_to_keep_up_btn = ttk.Button(self.mid_frame, text=">", command=lambda: self.change_pause_to_keep_duration_up(self), width=1)
        self.mid_pause_to_keep_entry = ttk.Entry(self.mid_frame, textvariable=self.minutes_of_pause_to_keep, width=4)

        # setup mid frame widgets
        mid_type_label.grid(row=0, column=0, columnspan=4)
        self.mid_ab_btn.grid(row=1, column=0, columnspan=3, sticky = W)
        self.mid_abc_btn.grid(row=2, column=0, columnspan=3, sticky = W)
        self.mid_abc2_btn.grid(row=3, column=0, columnspan=3, sticky = W)
        mid_conf_abc_a_label.grid(row=4, column=0)
        mid_conf_abc_b_label.grid(row=4, column=1)
        mid_conf_abc_c_label.grid(row=4, column=2)
        self.mid_abc_a_box.grid(row=5, column=0)
        self.mid_abc_b_box.grid(row=5, column=1)
        self.mid_abc_c_box.grid(row=5, column=2)

        mid_filler_label3.grid(row=6, column=0, columnspan=3)
        mid_pause_label.grid(row=7, column=0, columnspan=4, pady=5)
        self.mid_pause_entry.grid(row=8, column=0)
        self.mid_pause_slider.grid(row=8, column=1, sticky=W)
        mid_pause_dn_btn.grid(row=8, column=2, sticky=E)
        mid_pause_up_btn.grid(row=8, column=3, sticky=W)
        self.mid_pause_checkbox.grid(row=9, column=0, pady=4, columnspan=4)

        ## Pauses to Keep feature
        mid_pause_to_keep_label.grid(row=10, column=0, columnspan=4, pady=5)
        self.mid_pause_to_keep_entry.grid(row=11,column=0)
        self.mid_pause_to_keep_slider.grid(row=11, column=1, sticky=W)
        mid_pause_to_keep_dn_btn.grid(row=11, column=2, sticky=E)
        mid_pause_to_keep_up_btn.grid(row=11, column=3, sticky=W)
        self.mid_keep_pause_checkbox.grid(row=12,column=0, pady=4, columnspan=4)

        

        #self.mid_abc_a_box.update()
        #self.mid_abc_b_box.update()
        #self.mid_abc_c_box.update()

    def setup_btm_frame(self):
        """
        Configure bottom frame. Inlcudes progress bar, submit/cancel button, and message window.
        :return:
        """
        # BOTTOM FRAME CONFIG
        # create bottom frame widgets

        self.btm_submit_btn = ttk.Button(self.btm_frame, text="Submit", command=self.start_analysis)
        self.btm_progress_bar = ttk.Progressbar(self.btm_frame, orient=HORIZONTAL, length=170, mode='indeterminate')
        self.btm_text_window = None
        if platform.system() == MAC:
            self.btm_text_window = Text(self.btm_frame, width=45, height=5)
        elif platform.system() == WINDOWS:
            self.btm_text_window = Text(self.btm_frame, width=34, height=5)
	elif platform.system() == LINUX:
            self.btm_text_window = Text(self.btm_frame, width=34, height=5)
        self.btm_text_window.config(state=DISABLED)

        # arrange bottom frame widgets
        self.btm_submit_btn.grid(row=0, column=0, sticky=E)
        self.btm_progress_bar.grid(row=0, column=0, sticky=W)
        self.btm_text_window.grid(row=1, column=0, columnspan=1)

    def select_input_dir(self):
        """
        Updates input_dir variable. Bound to top_in_browse_btn.
        :return:
        """
        self.file_dict.clear()
        input_dir = tkFileDialog.askdirectory()
        if input_dir:
            self.input_dir.set(input_dir)
            self.get_files()
            self.get_labels()
            for code in code_use:
                code_use[code] = False
            #self.mid_abc_a_box.update()
            #self.mid_abc_b_box.update()
            #self.mid_abc_c_box.update()

    def select_output_dir(self):
        """
        Updates output_dir variable. Bound to top_out_browse_btn.
        :return:
        """
        output_dir = tkFileDialog.askdirectory()
        if output_dir:            
            self.output_dir.set(output_dir)

    def get_files(self):
        """
        This method looks creates a dict of all .its files found in the input directory
        :return:
        """
        # ************************************
        tempDict = Batch(self.input_dir.get())
        for i in range(len(tempDict.items)):
            tempItem = tempDict.items.popitem()
            self.file_dict.update({tempItem[0]:tempItem[1][0]})

    def check_config(self):
        """
        This method checks if all seq_config values are set. Returns error message if any aren't set.
        :return status of current configuration's validity:
        """
        # check input directory
        if len(str(self.top_in_path.get())) < 2:
            return "Input directory not set! "

        # check output directory
        if len(str(self.top_out_path.get())) < 2:
            return "Output directory not set! "

        # check sequence_type
        if str(self.sequence_type.get()) not in (AB, ABC, ABC2):
            return "Sequence Type not set! "

        # check var_a
        if not self.var_a:
            return "A is not set! "

        # check var_b
        if not self.var_b:
            return "B is not set! "

        # check var_c
        if (self.sequence_type.get() == ABC or self.sequence_type.get() == ABC2):
            if not self.var_c:
                return "C is not set! "

        # check output_format
        if not self.output_format:
            return "Output format not set! "
        else:
            self.write_to_window("All config options are valid!")
        
        return OK

    def set_config(self):
        """
        This method sets the self.seq_config variable - returns True if successful, False if unsuccessful
        :return True or False for configuration set-up:
        """
        # check if config options set
        errorVal = self.check_config()
        if errorVal != OK:
            self.write_to_window(errorVal)
            return False

        # all config options set, so fill self.seq_config
        self.seq_config['batDir'] = self.top_in_path.get()
        self.seq_config['A'] = ','.join(map(str, self.var_a)) 
        self.seq_config['B'] = ','.join(map(str, self.var_b))
        self.seq_config['C'] = ','.join(map(str, self.var_c))
        self.seq_config['outputContent'] = ""
        self.seq_config['roundingEnabled'] = str(self.rounding_enabled.get())
        self.seq_config['keepAllPauses'] = str(self.keep_pauses.get())
        self.seq_config['P'] = 'Pause'
        self.seq_config['outputDirPath'] = self.top_out_path.get()
        self.seq_config['seqType'] = self.sequence_type.get()
        self.seq_config['PauseDur'] = str(round(self.pause_duration.get(), 1))
        self.seq_config['PauseKeep'] = str(round(self.minutes_of_pause_to_keep.get(), 1))
        self.seq_config['outputTypes'] = ''.join(self.output_format)

        self.write_to_window("Config options assembled!")
        return True

    def kill_threads(self):
        """
        Sends stop message to all threads and updates UI.
        :return:
        """
        # set stopper - threads will close
        self.stopper.set()

        # update UI
        self.btm_submit_btn.configure(text="Submit", command=self.start_analysis)
        #self.enable_widgets()
        self.btm_progress_bar.stop()

    def watch_status(self):
        """
        This method watches for analysis finish or user cancel. Started after pressing the submit button, but not
        before checking+setting seq_config.
        :return:
        """
        while True:
            if len(self.seq_run_results) > 0:
                # configure UI
                self.btm_submit_btn.configure(text="Submit", command=self.start_analysis)
                #self.enable_widgets()
                self.btm_progress_bar.stop()
                self.write_to_window(self.seq_run_results[0] + " Ran in "+str(round(time.time()-self.start_time,2))+"s")

                # reset check var
                self.seq_run_results = []
                self.stopper = None
                break
            elif self.stopper.is_set():
                # alert user
                self.write_to_window("Analysis Cancelled!")

                # reset check var
                self.seq_run_results = []
                self.stopper = None
                break

    def start_analysis(self):
        """
        Starts run_seqanalysis thread. run_seqanalysis needs to be run as a thread so we don't interrupt the main
        UI thread.
        :return:
        """
        # setup
        self.stopper = threading.Event()
        self.btm_submit_btn.configure(state=DISABLED)

        # start analysis thread
        t = threading.Thread(target=self.run_seqanalysis)
        t.daemon = True
        t.start()

    def run_seqanalysis(self):
        """
        This method performs the sequence analysis on all .its/csv files
        :return:
        """
        # setup
        self.start_time = time.time()
        #self.disable_widgets()
        self.btm_progress_bar.start()

        # check config
        start = time.time()
        r = self.set_config()
        if r != True:
            # set_config already output to window
            self.btm_submit_btn.configure(text="Submit", command=self.start_analysis)
            self.btm_submit_btn.configure(state='enable')
            self.btm_progress_bar.stop()
            #self.enable_widgets()
            return 
        
        # retrieve .its files
        #self.get_files()
        if len(self.file_dict) < 1:
            self.write_to_window("No .its or .csv files in input directory!")
            self.btm_submit_btn.configure(text="Submit", command=self.start_analysis)
            self.btm_submit_btn.configure(state='enable')
            self.btm_progress_bar.stop()
            #self.enable_widgets()
            return

        # start watcher thread
        th = threading.Thread(target=self.watch_status)
        th.daemon = True
        th.start()

        # enable cancel button
        self.btm_submit_btn.configure(state='enable')
        self.btm_submit_btn.configure(text="Cancel", command=self.kill_threads)

        # create object to send to analysis
        data = SeqData(self.file_dict, self.seq_config, self.num_threads.get(), self.output_format)
        self.seq_run_results = []

        # kick off analysis 
        thread = threading.Thread(target=SeqAnalysis, args=(data,self.seq_run_results, self.stopper))
        thread.daemon = True
        thread.start()
         
    def load_config(self):
        """
        This method loads a config file for the program
        :return:
        """
        
        # file dialog - select file
        config_load_file = tkFileDialog.askopenfilename(initialdir="/", title="Select config file", filetypes=(("leco files", "*.leco"), ("all files", "*.*")))
        if not str(config_load_file).endswith('.leco'):
            return
        
        print("Loaded File")

        # open file 
        new_config = None
        try:
            open_file = open(config_load_file, 'r')
            new_config = ast.literal_eval(open_file.read())
            assert type(new_config) is dict
            open_file.close()
        except:
            self.write_to_window("Failed to Load File!") 
            return
        print("Loaded file to config")
        
        # check contents
        try:
            # check batDir
            if(len(new_config['batDir']) < 2):
                raise Exception("batDir invalid")
            
            # check outputDir
            if(len(new_config['outputDirPath']) < 2):
                raise Exception("Invalid outputDirPath!")

            # check SeqType
            if new_config['seqType'] == AB:
                pass
            elif new_config['seqType'] == ABC:
                pass
            elif new_config['seqType'] == ABC2:
                pass
            else:
                raise Exception("seqType Invalid")
            
            # check A
            if not any(x in codes for x in new_config['A'].split(',')):
                raise Exception("Invalid Var A")

            # check B
            if not any(x in codes for x in new_config['B'].split(',')):
                raise Exception("Invalid Var B")

            # check C
            if(new_config['seqType'] == ABC or new_config['seqType'] == ABC2):
                if not any(x in codes for x in new_config['C'].split(',')):
                    raise Exception("Invalid Var C")

            # check rounding enabled
            if new_config['roundingEnabled'] == 'True':
                pass
            elif new_config['roundingEnabled'] == 'False':
                pass
            else:
                raise Exception("Invalid roundingEnabled!")

            # check pause
            #if(new_config['Pause'] != 'Pause'):
            #    raise Exception("Invalid P")

            # check pause duration
            if(float(new_config['PauseDur']) < 0.1 ):
                raise Exception("Invalid pause duration!")

            # check output formats
            if not any(x in new_config['outputTypes'] for x in ['csv', 'xlsx', 'txt']):
                raise Exception("Invalid output types!")
            
        except Exception as e:
            self.write_to_window("FAILURE! Invalid file contents!")
            print(repr(e))
            return
        print("Config contents checked")

        # fill contents to program
        self.reset_config()
        
        ## Fill Vars + seqConfig
        try:
            self.seq_config['batDir'] = new_config['batDir']            

            self.seq_config['A'] =  new_config['A']
             
            self.seq_config['B'] = new_config['B']

            self.seq_config['C'] = new_config['C']     

            self.seq_config['roundingEnabled'] = new_config['roundingEnabled']            
            
            self.seq_config['outputDirPath'] = new_config['outputDirPath']

            self.seq_config['seqType'] = new_config['seqType']        

            self.seq_config['PauseDur'] = new_config['PauseDur']            

            self.seq_config['outputTypes'] = new_config['outputTypes']
            self.output_format = []

            if 'xlsx' in new_config['outputTypes']:
                self.output_format.append(".xlsx")               
            if 'csv' in new_config['outputTypes']:
                self.output_format.append(".csv")                
            if 'txt' in new_config['outputTypes']:
                self.output_format.append(".txt")
                
            self.seq_config['outputContent'] = ""
            self.seq_config['P'] = 'Pause'
            
            print("Program variables filled")
        except Exception as e:
            #self.write_to_window("")
            print(repr(e))
            return
        

        ## Fill Widgets        
        try:
            # input and output
            self.input_dir.set(new_config['batDir'])
            self.output_dir.set(new_config['outputDirPath'])
            
            # output formats
            if 'txt' in new_config['outputTypes']:
                self.txt_var.set(1)
            else:
                self.txt_var.set(0)

            if 'csv' in new_config['outputTypes']:
                self.csv_var.set(1)
            else:
                self.csv_var.set(0)

            if 'xlsx' in new_config['outputTypes']:
                self.xl_var.set(1)
            else:
                self.xl_var.set(0)

            # sequence type
            self.sequence_type.set(new_config['seqType'])
            
            # var_a/b/c
            #self.mid_abc_a_box
            var_a_list = new_config['A'].split(',')
            for item in var_a_list:
                self.mid_abc_a_box.selection_set(codes_index[item])
                self.var_a.append(item)
            
            #self.mid_abc_b_box
            var_b_list = new_config['B'].split(',')            
            for item in var_b_list:
                self.mid_abc_b_box.select_set(codes_index[item])
                self.var_b.append(item)

            #self.mid_abc_c_box
            if (new_config['seqType'] == ABC or new_config['seqType'] == ABC2):
                var_c_list = new_config['C'].split(',')
                for item in var_c_list:
                    self.mid_abc_c_box.select_set(codes_index[item])
                    self.var_c.append(item)
            else:
                self.mid_abc_c_box.configure(state="disable")
                self.mid_abc_c_box.update()

            # pause duration
            self.pause_duration.set(float(new_config['PauseDur']))
            self.minutes_of_pause_to_keep.set(float(new_config['PauseKeep']))

            # rounding enabled           
            if new_config['roundingEnabled'] == 'True':
                self.rounding_enabled.set(True)

            # keep all pauses enabled
            if new_config['keepAllPauses'] == 'True':
                self.keep_pauses.set(True)
                self.minutes_of_pause_to_keep.set(1)
            else:
                self.keep_pauses.set(False)

        except Exception as e:
            print(repr(e))
            print("FAILED TO FILL WIDGETS ON LOAD!")

        print("Program Widgets filled")

        # write results to screen
        self.write_to_window("Successfully Loaded config file!")

    def reset_config(self):
        """
        This method resets the all program options
        :return:
        """
        # re-initialize key variables used in the UI
        self.input_dir = StringVar()
        self.output_dir = StringVar()
        self.sequence_type = StringVar()
        self.pause_duration = DoubleVar()
        self.minutes_of_pause_to_keep = DoubleVar()
        self.pause_duration.set(0.1)
        self.minutes_of_pause_to_keep.set(0.0)

        # re-initialize the A, B, & C entry boxes
        self.mid_abc_a_box.select_clear(0,END)
        self.mid_abc_b_box.select_clear(0,END)
        self.mid_abc_c_box.select_clear(0,END)
        self.var_a = []
        self.var_b = []
        self.var_c = []

        # re-initialize the selections
        self.output_format = []
        self.output_format.append(".csv")
        self.csv_var.set(1)
        self.txt_var.set(0)
        self.xl_var.set(0)
        self.rounding_enabled.set(0)
        self.keep_pauses.set(1)

        # re-initialize the selections update
        self.top_csv_btn.configure(variable=self.csv_var)
        self.top_txt_btn.configure(variable=self.txt_var)
        self.top_xl_btn.configure(variable=self.xl_var)
        self.mid_pause_checkbox.configure(variable=self.rounding_enabled)
        self.mid_keep_pause_checkbox.configure(variable=self.keep_pauses)
        self.top_csv_btn.update()
        self.top_txt_btn.update()
        self.top_xl_btn.update()
        self.mid_pause_checkbox.update()
        self.mid_keep_pause_checkbox.update()
    
        # reset the in and out dir update
        self.top_in_path.configure(textvariable=self.input_dir)
        self.top_out_path.configure(textvariable=self.output_dir)
        self.top_in_path.update()
        self.top_out_path.update()

        # reset the selection to nothing selected update
        self.mid_ab_btn.configure(variable=self.sequence_type)
        self.mid_abc_btn.configure(variable=self.sequence_type)
        self.mid_abc2_btn.configure(variable=self.sequence_type)
        self.mid_ab_btn.update()
        self.mid_abc_btn.update()
        self.mid_abc2_btn.update()

        # reset slider and pause_duration entry box update
        self.mid_pause_slider.configure(variable=self.pause_duration)
        self.mid_pause_entry.configure(textvariable=self.pause_duration)
        self.mid_pause_to_keep_slider.configure(variable=self.minutes_of_pause_to_keep)
        self.mid_pause_to_keep_entry.configure(textvariable=self.minutes_of_pause_to_keep)
        self.mid_pause_slider.update()
        self.mid_pause_entry.update()
        self.mid_pause_to_keep_entry.update()
        self.mid_pause_to_keep_slider.update()
        
    def save_config(self):
        """
        This method allows the user to save the program's current configuration
        :return:
        """
        if self.check_config() == OK:
            self.set_config()
            config_save_file = tkFileDialog.asksaveasfile(mode='w', defaultextension=".leco")
            seq_config_string = str(self.seq_config)
            config_save_file.write(seq_config_string)
            self.write_to_window("Configuration successfully saved! ")
        else:
            self.write_to_window("Unfilled configuration options!")
            
    def load_instruction_window(self):
        """
        This method loads a separate window with program instructions
        :return:
        """
        instruction_var = self.list_instructions() 
        tkMessageBox.showinfo("Instructions",self.list_instructions())

    def close_program(self):
        """
        This method closes the program
        :return:
        """
        self.root.quit()
    
    def write_to_window(self, message):
        """
        This method writes text to message box
        :param message:
        :return:
        """

        # edit message text
        self.output_msg_counter += 1
        message = str(self.output_msg_counter)+": "+message +'\n'
        self.output_msg = message + self.output_msg

        # insert text
        # we must enable window to edit contents
        self.btm_text_window.config(state=NORMAL)
        self.btm_text_window.delete(1.0,END)
        self.btm_text_window.insert(END, self.output_msg)
        self.btm_text_window.config(state=DISABLED)

    def set_output_var(self):
        """
        This method sets the output var based on the user's selection
        :return:
        """

        if self.csv_var.get() == 1:
            if ".csv" not in self.output_format:
                self.output_format.append(".csv")
        elif self.csv_var.get() == 0:
            if ".csv" in self.output_format:
                self.output_format.remove(".csv")

        if self.xl_var.get() == 1:
            if ".xlsx" not in self.output_format:
                self.output_format.append(".xlsx")
        elif self.xl_var.get() == 0:
            if ".xlsx" in self.output_format:
                self.output_format.remove(".xlsx")
        
        if self.txt_var.get() == 1:
            if ".txt" not in self.output_format:
                self.output_format.append(".txt")
        elif self.txt_var.get() == 0:
            if ".txt" in self.output_format:
                self.output_format.remove(".txt")
    
    def disable_widgets(self):
        """
        This method disables top and mid widgets
        :return:
        """
        for child in self.top_frame.winfo_children():
            try:
                child.configure(state=DISABLED)
            except:
                pass
        for child in self.mid_frame.winfo_children():
            try:
                child.configure(state=DISABLED)
            except:
                pass

    def enable_widgets(self):
        """
        This method enables top and mid widgets
        :return:
        """
        for child in self.top_frame.winfo_children():
            try:
                child.configure(state='normal')
            except:
                pass
        for child in self.mid_frame.winfo_children():
            try:
                child.configure(state='normal')
            except:
                pass
        
        # Listbox reset
        self.mid_abc_a_box.configure(state="normal")
        self.mid_abc_a_box.update()
        self.mid_abc_b_box.configure(state="normal")
        self.mid_abc_b_box.update()
        self.mid_abc_c_box.configure(state="normal")
        self.mid_abc_c_box.update()

        # conditional seqType
        if self.sequence_type.get() == AB:
            self.mid_abc_c_box.configure(state="disable")
            self.mid_abc_c_box.update()
    
    def list_instructions(self):
        """
        Puts together the user instructions.
        :return string - user instructions:
        """
        instruction_var = "1) SAVE:  \n\tSaves all the data currently in all fields.\n"
        instruction_var += "2) LOAD:  \n\tLoads the data last saved in all fields.\n"
        instruction_var += "3) RESET:  \n\tEmpties all fields\n"
        instruction_var += "4) INPUT:  \n\tBrowse to the directory that contains all files for analysis\n"
        instruction_var += "5) OUTPUT:  \n\tBrowse to the desired directory for the output file\n"
        instruction_var += "6) OUTPUT FORMAT:  \n\tSelect the desired format for output file\n"
        instruction_var += "7) TYPE OF ANALYSIS:  \n\tChoose the type of analysis to be done and its variables:\n"
        instruction_var += "\tA--->B  or  (A---> B)---> C: type of analysis performed:\n"
        instruction_var += "\tA, B, C:  Drop down menus to select desired variables\n"
        instruction_var += "8) PAUSE DURATION:  \n\tUse entry field, slider bar, and/or buttons to choose pause duration\n"
        instruction_var += "\tEntry field:  enter in specific pause duration in seconds and tenths of seconds\n"
        instruction_var += "\tSlider bar:  Click and hold to move along bar\n"
        instruction_var += "\tButtons(<,>):  Moves slider bar by 0.1 seconds in specified direction\n"
        instruction_var += "9) ENABLE ROUNDING:  \n\tSelect to enable rounding to nearest integer with tie-breaking threshold of 0.5 seconds\n"
        instruction_var += "10) SUBMIT:  \n\tSubmits the current data in fields to the program to start analysis\n"
        return instruction_var
