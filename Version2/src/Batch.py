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

The purpose of this module is to load all the files from the chosen directory and create a dictionary of file and id pairs.
"""

from os import listdir
from os.path import isfile, join, splitext
#import pandas as pd
import xml.etree.ElementTree as ET

class Batch:
	def __init__(self,batDir):
		"""
		Initializes the loading of files from the batch directory.
		:param batDir:
		"""
		self.items = {} # key:username, value:filename
		self.LoadData(batDir)
		self.increment = 0

	def LoadData(self,batDir):
		"""
		Loads files from the chosen batch directory and sets up dictionary based on file type.
		Currently supports .its and .csv file type for analysis.
		:param batDir:
		:return:
		"""
		# List all files in specified directory
		allfiles = [fname for fname in listdir(batDir) if isfile(join(batDir,fname))]

		# Store only .its and/or .csv files in map
		for f in allfiles:
			if ".its" in f:
				#Load xml tree to get subject ID
				fullpath = join(batDir, f)
				tree = ET.parse(fullpath)
				subID = 'no subject ID'
				try:
					subInfoNode = tree.find("ExportData/Child") #TODO: evidently, not all ITS files have this node. tentative solution implemented
					subID = subInfoNode.attrib["id"]
				except:
					print '+++ .its file does not contain ExportData/Child node. Setting subject ID to \'no subject ID \''
				
				# Add a new subject ID and filename to the map
				if subID not in self.items:
					self.items[subID] = []
					self.items[subID].append(fullpath)
				else:
					uniqueID = self.EnsureUnique(subID)
					self.items[uniqueID] = []
					self.items[uniqueID].append(fullpath)
			"""
			# we are currently ignoring .csv files as input at the request of Dr. Yoder
			if ".csv" in f:
				csv_path = join(batDir, f)
				csvID = splitext(f.split('_')[-1])[0] # getting csvID by splitting on '_' and removing extension (last term is child id)

				if csvID not in self.items:
					self.items[csvID] = []
					self.items[csvID].append(csv_path)
				else:
					uniqueID = self.EnsureUnique(csvID)
					self.items[uniqueID] = []
					self.items[uniqueID].append(csv_path)
			"""

	def EnsureUnique(self,ID):
		"""
		Modifies the specified ID using a monotonically increasing scheme.
		"""
		newID = ''
		if '_' in ID:
			compsID = ID.split('_')
			newIDNum = int( compsID[1] ) + 1
			newID = comps[0] + '_' + str(newIDNum)
		else:
			self.increment += 1
			newID = ID + '_' + str(self.increment)

		return newID
				 
