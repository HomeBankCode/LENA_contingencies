"""
The MIT License (MIT)
Copyright (c) 2016 Paul Yoder, Joshua Wade, Jon Tapp, Anne Warlaumont, and Amy Harbison

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from Tkinter import *
from Automata import Automaton
from Batch import Batch
from LoadBatchDlg import LoadBatchDlg
from SeqDesDlg import *
from PauseDesDlg import PauseDesDlg
from SeqAnalysis import SeqAnalysis
from GetOutputDirDlg import GetOutputDirDlg


VERBOSE = True

class SupervisoryController(Automaton):
	def __init__(self):
		Automaton.__init__(self,VERBOSE)
		# Define States
		self.INIT = 0
		self.GET_BATCH_CFG = 1
		self.DESIGN_SEQ = 2
		self.DESIGN_PAUSE = 3
		self.PERF_ANALYSIS = 4
		self.LOG_RESULTS = 5
		self.COMPLETE = 6
		# Initial Transition
		self.Transition( self.INIT )

def main():
	# Create Automaton object for the Supervisory Controller behavior
	scFSM = SupervisoryController()
	
	# Create Batch oject for processing
	batch = None

	# Create a variable map object to pass between dialog windows
	varMap = {}

	# Begin main loop
	print 'Launching .../LENA_contingencies/control.py'
	while( True ):
		# INITIALIZE ESSENTIAL OBJECTS
		if scFSM.state_curr is scFSM.INIT:
			# init variable map keys
			varMap["P"]="P"
			varMap["outputContent"]=""
			varMap["outputDirPath"]=""		
			
			# enact transition to the next state
			scFSM.Transition( scFSM.GET_BATCH_CFG )

		# PROMPT USER FOR BATCH CONFIG FILES
		elif scFSM.state_curr is scFSM.GET_BATCH_CFG:
			# Launch LoadBatchDlg
			Launch('LoadBatchDlg', 'Load Batch Directory Files', varMap)

			# Initialize Batch object
			batch = Batch(varMap["batDir"])
			
			# enact transition to the next state
			scFSM.Transition( scFSM.DESIGN_SEQ )

		# PROMPT USER TO DESIGN ANTECEDENT/CONSEQUENT SEQ
		elif scFSM.state_curr is scFSM.DESIGN_SEQ:
			# Launch SeqDesDlg
			Launch('SeqDesDlg','Sequence Design', varMap)
			print 'Sequence type selected is ' + varMap["seqType"]

			# Launch Antecedent-->Consequent Design Dialog (AntConDesDlg)
			Launch('AntConDesDlg','Ant/Con Design', varMap)
			
			# enact transition to the next state
			scFSM.Transition( scFSM.DESIGN_PAUSE )

		# PROMPT USER TO DESIGN PAUSES TO INSERT
		elif scFSM.state_curr is scFSM.DESIGN_PAUSE:
			# Launch PauseDesDlg
			Launch('PauseDesDlg','Pause Design', varMap)
			
			# enact transition to the next state
			scFSM.Transition( scFSM.PERF_ANALYSIS )

		# PERFORM SEQ ANALYSIS
		elif scFSM.state_curr is scFSM.PERF_ANALYSIS:
			print 'Beginning sequential analysis with conditions: ' + str(varMap)
			print 'Batch contains: ' + str(batch)
			# Perform analyses
			for k,v in batch.items.iteritems():
				sa = SeqAnalysis(varMap, k, v)
							
			# enact transition to the next state
			scFSM.Transition( scFSM.LOG_RESULTS )

		# PROMPT USER TO SPECIFIY LOCATION TO WRITE RESULTS
		elif scFSM.state_curr is scFSM.LOG_RESULTS:	
			# Launch GetOutputDirDlg
			Launch('GetOutputDirDlg','Specify Output Directory', varMap)

			# Write results to file
			f = open(varMap["outputDirPath"]+'/'+GetFileTitle(varMap),'a')
			f.write(varMap["outputContent"])
			f.close()

			# enact transition to the next state
			scFSM.Transition( scFSM.COMPLETE )

		# TASK COMPLETE: DISPLAY APP RESULTS TO USER AND EXIT
		elif scFSM.state_curr is scFSM.COMPLETE:
			break

	# Wrap up and exit
	print 'Process completed. Exiting...'

def Launch(dlgName, title, varMap):
	root = Tk()
	root.geometry('%dx%d+%d+%d' % (800, 200, 0, 0))
	dlg = None

	if dlgName is 'LoadBatchDlg':
		dlg = LoadBatchDlg(master=root,_varMap=varMap)
	elif dlgName is 'SeqDesDlg':
		dlg = SeqDesDlg(master=root,_varMap=varMap)
	elif dlgName is 'AntConDesDlg':
		dlg = AntConDesDlg(master=root,_varMap=varMap)
	elif dlgName is 'PauseDesDlg':
		dlg = PauseDesDlg(master=root,_varMap=varMap)
	elif dlgName is 'GetOutputDirDlg':
		dlg = GetOutputDirDlg(master=root,_varMap=varMap)

	dlg.master.title(title)
	dlg.mainloop()
	root = None

def GetFileTitle(varMap):
	t = 'batch_'
	t += varMap["seqType"]
	t += '_pause=' + varMap["PauseDur"]
	t += 's_analysisDate=' + MMDDYYYY(delim='-')
	t += '.csv'
	return t

from datetime import datetime
def MMDDYYYY(delim="/"):
        t = datetime.now()
        dateStr = str(t.month) + delim
        dateStr += str(t.day) + delim
        dateStr += str(t.year)
        
        return dateStr

#program entry point
main()
