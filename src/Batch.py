"""
The MIT License (MIT)
Copyright (c) 2016 Paul Yoder, Joshua Wade, Jon Tapp, Anne Warlaumont, and Amy Harbison

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET

class Batch:
	def __init__(self,batDir):
		self.items = {} # key:username, value:filename
		self.LoadData(batDir)

	def LoadData(self,batDir):
		# List all files in specified directory
		allfiles = [fname for fname in listdir(batDir) if isfile(join(batDir,fname))]

		# Store only .its files in map
		for f in allfiles:
			if ".its" in f:
				#Load xml tree to get subject ID
				fullpath = join(batDir, f)
				tree = ET.parse(fullpath)
				subInfoNode = tree.find("ExportData/Child")
				subID = subInfoNode.attrib["id"]
				
				# Add a new subject ID and filename to the map
				if subID not in self.items:
					self.items[subID] = []
				self.items[subID].append(fullpath)
