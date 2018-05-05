"""
The MIT License (MIT)
Copyright (c) 2016 Paul Yoder, Joshua Wade, Jon Tapp, Anne Warlaumont, and Amy Harbison

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from Tkinter import *
import tkFileDialog

class LoadBatchDlg( Frame ):
	def __init__(self,master=None,_varMap={}):
		Frame.__init__(self,master)
		self.mstr = master
		self.createWidgets()
		self.pack()
		self.batDir = ''
		self.varMap=_varMap

	def createWidgets(self):
		self.Load = Button(self)
		self.Load["command"] = self.PromptFile
		self.Load["text"] = 'Please specify the batch directory.'
		self.Load.pack()

	def PromptFile(self):
		print 'Requesting input directory...'
		self.batDir = tkFileDialog.askdirectory()
		if self.batDir is not '':
			print 'Loading batch files from ' + str(self.batDir)
			self.varMap["batDir"] = self.batDir
		self.master.destroy()
