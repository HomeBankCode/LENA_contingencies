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

Takes the SeqData object and performs the actual logic of the sequence analysis. It generates an event item list,
removes and adds required pauses to the item list, performs sequence analysis, generates an output string,
calculates the ocv, and finally, logs errors.
"""

import xml.etree.ElementTree as ET
from copy import deepcopy
import os
import csv
import threading
import Queue
from Helpers import *
import math

# Event Item
class EItem:
	"""
	Event Item Object class
	"""
	def __init__(self, spkr, onset, offset):
		"""
		Initializes the event item with an xml attribute.
		:param attr:
		"""
		self.spkr = spkr
		self.onset = onset
		self.offset = offset


# Event Item List
class EItemList:
	"""
	Event Iten List Object
	"""
	def __init__(self, _varMap={}, pid=0, filename=''):
		"""
		Initializes the Event Item List with the varmap (A, B, C, D), the pid represents the id associated with the file,
		and the file name.

		:param _varMap:
		:param pid:
		:param filename:
		"""
		self.list = []
		self.list_ = []
		self._varMap = _varMap
		self.seqType = self._varMap["seqType"]
		self.pid = pid
		self.filename = filename
		self.relevantSpkrs = self._varMap["A"]+','+self._varMap["B"]+','+self._varMap["C"]+',Pause'
		self.pauseDur = float(self._varMap["PauseDur"])
		self.pauseKeep = float(self._varMap["PauseKeep"])
		self.keepAllPauses = True if "1" in self._varMap["keepAllPauses"] else False
		self.eventCnt = {"A":0,"B":0,"C":0,"P":0}
		self.evTypes = ["A","B","C","P"]
		self.contingencies = {"a":0, "b":0, "c":0, "d":0}
		self.round = True if "1" in self._varMap["roundingEnabled"] else False

	def AddEItem(self, seg, flag=None):
		"""
		Adds an event item to the event item list. Completes check for CHN events.
		Seg is a segment that is parses out of the xml tree, flag is for signaling terminal or initial segment of the
		file.

		:param seg:
		:param flag:
		:return:
		"""
		# Specify CHN events as either CHNSP or CHNNSP events
		if 'CHN' in seg.attrib["spkr"]:
			seg.attrib["spkr"] = self.Modify_CHN_Events(seg)

		# Handle first and last events in .its file if they aren't relevant speakers
		if (flag is 'Initial' or flag is 'Terminal') and seg.attrib["spkr"] not in self.relevantSpkrs:
			seg.attrib["spkr"]="Pause"
		if seg.attrib["spkr"] in self.relevantSpkrs:
			self.list.append( EItem(seg.attrib["spkr"], float(seg.attrib["startTime"][2:-1]), float(seg.attrib["endTime"][2:-1])) )

	def AddEItemCSV(self, data_array, flag=None):
		"""
		Adds an event item from CSV data to the event item list.
		"""
		#CSV items should be interpreted as instantaneous events and thus will not have durations.
		if(flag is 'Initial' or flag is 'Terminal') and data_array[1] not in self.relevantSpkrs:
			data_array[1] = "Pause"
		if data_array[1] in self.relevantSpkrs:
			onsetTS = data_array[0].split(':')
			onset = int(onsetTS[0])*60*60 + int(onsetTS[1])*60 + int(onsetTS[2]) + int(onsetTS[3])/100
			offset = onset
			self.list.append( EItem(data_array[1], onset, offset) )

	def Modify_CHN_Events(self, seg):
		"""
		Handles special case of CHN events, determines which one they are.
		:param seg:
		:return string representing the type of CHN event:
		"""
		CHN_mod = ''
		if 'startUtt1' in seg.attrib:
			CHN_mod = 'CHNSP'
		else:
			CHN_mod = 'CHNNSP'
		return CHN_mod

	def Size(self):
		"""
		Returns current size of the Event item list.
		:return the current integer length of the event item list:
		"""
		return len(self.list)

	def GetItem(self, index):
		"""
		Returns the event item from the event item list at the given index.
		:param index:
		:return Event item from the event item list:
		"""
		return self.list[index]

	def RemoveExtraneousPauses(self):
		"""
		Removes inserted contiguous pauses that are past a user specified amount of pauses to keep. 
		For instance, if there are 11 minutes of contiguous pauses, but the user only wants to keep 10,
		then 1 minute of pauses will be removed
		:return:
		"""
		
		timeOfContiguousPauses = 0.0
		unwantedPauses = []
		secondsToKeep = int(self.pauseKeep * 60)

		for item in self.list:
			
			if (item.spkr != 'Pause'):
				timeOfContiguousPauses = 0.0

			if (item.spkr == 'Pause'):
				timeOfContiguousPauses += (item.offset - item.onset)

			if (timeOfContiguousPauses > secondsToKeep) and (item.spkr == 'Pause'):
				unwantedPauses.append(item)

		print '+++ Num pauses removed = ' + str(len(unwantedPauses))
		for pause in unwantedPauses:
			self.list.remove(pause)	

	def InsertPauses(self, CSV = False):
		"""
		Inserts pauses into the event item list.
		Specifies the size of the ouases from the slider in the UI.
		:return:
		"""
		self.list_.append(deepcopy(self.list[0]))
		for i in range(1,self.Size()):
			#determine whether to add pause before copying event
			P = self.pauseDur
			curEvT = self.list[i].onset
			preEvT = self.list[i - 1].offset
			eT = curEvT - preEvT

			if (not CSV and eT >= P) or (CSV and eT > P):
				# calculate number of pauses to insert
				numP = 0
				if not CSV:
					if self.round is True:
						try:
							numP = int( (eT / P) + .5 )
						except ZeroDivisionError:
							numP = 0
					else:
						try:
							numP = int( (float(eT) / float(P)) )
						except ZeroDivisionError:
							numP = 0
				else:
					try:
						numP = int( (eT/P) )
					except:
						numP = 0

				for j in range(0,numP):
					# insert pause
					startTime = preEvT+(j*P)
					endTime = min(curEvT,startTime+P)
					self.list_.append( EItem("Pause", startTime, endTime) )
			#add current event
			self.list_.append( deepcopy(self.list[i]) )

		#free memory used by interim list
		self.list = deepcopy(self.list_)
		self.list_ = None

	def TallyItems(self):
		"""
		Counts up the number of each event type.
		:return:
		"""
		for i in range(0, self.Size()): # iterate over Event Items
			for e in self.evTypes:			
				if self.list[i].spkr in self._varMap[e]:
					self.eventCnt[e] += 1

	"""def PrintList(self):
		contentToWrite = []
		for i in range(0, self.Size()):
			contentToWrite.append( str(self.list[i].onset)+","+str(self.list[i].spkr) )

		f = open('/your/path/here/seq.csv', 'w') #For debugging
		f.write('\n'.join(contentToWrite))
		f.close()"""

	def SeqAn(self):
		"""
		Primary the function for completed the logic of the given sequence analysis.
		Checks the var map and decides which contingency to increment based on the chosen logical expression.
		:return:
		"""
		numItems = self.Size()
		# A-->B
		if self._varMap['seqType'] == 'A_B':
			print 'A-->B Analysis in progress...'
			# iterate over event items
			for i in range(0, numItems-1):
				curr = self.list[i]
				next = self.list[i+1]
				if curr.spkr in self._varMap["A"] and next.spkr in self._varMap["B"]:
					self.contingencies["a"] += 1
				elif curr.spkr in self._varMap["A"] and next.spkr not in self._varMap["B"]:
					self.contingencies["b"] += 1
				elif curr.spkr not in self._varMap["A"] and next.spkr in self._varMap["B"]:
					self.contingencies["c"] += 1
				elif curr.spkr not in self._varMap["A"] and next.spkr not in self._varMap["B"]:
					self.contingencies["d"] += 1
		# (A-->B)-->C
		elif self._varMap['seqType'] == 'AB_C':
			print '(A-->B)-->C Analysis in progress...'
			# iterate over event items
			for i in range(0, numItems-2):
				curr = self.list[i]
				nextB = self.list[i+1]
				nextC = self.list[i+2]
				if curr.spkr in self._varMap["A"] and nextB.spkr in self._varMap["B"] and nextC.spkr in self._varMap["C"]:
					self.contingencies["a"] += 1
				elif curr.spkr in self._varMap["A"] and nextB.spkr in self._varMap["B"] and nextC.spkr not in self._varMap["C"]:
					self.contingencies["b"] += 1
				elif not(curr.spkr in self._varMap["A"] and nextB.spkr in self._varMap["B"]) and nextC.spkr in self._varMap["C"]:
					self.contingencies["c"] += 1
				elif not(curr.spkr in self._varMap["A"] and nextB.spkr in self._varMap["B"]) and nextC.spkr not in self._varMap["C"]:
					self.contingencies["d"] += 1

		# A-->(B-->C)
		elif self._varMap['seqType'] == 'A_BC':
			print 'A-->(B-->C) Analysis in progress...'
			# iterate over event items
			for i in range(0, numItems - 2):
				curr = self.list[i]
				nextB = self.list[i + 1]
				nextC = self.list[i + 2]
				if curr.spkr in self._varMap["A"] and nextB.spkr in self._varMap["B"] and nextC.spkr in self._varMap["C"]:
					self.contingencies["a"] += 1
				elif curr.spkr in self._varMap["A"] and not (nextB.spkr in self._varMap["B"] and nextC.spkr in self._varMap["C"]):
					self.contingencies["b"] += 1
				elif curr.spkr not in self._varMap["A"] and nextB.spkr in self._varMap["B"] and nextC.spkr in self._varMap["C"]:
					self.contingencies["c"] += 1
				elif curr.spkr not in self._varMap["A"] and not (nextB.spkr in self._varMap["B"] and nextC.spkr in self._varMap["C"]):
					self.contingencies["d"] += 1

	def Header(self):
		"""
		Assembles Headings string for output file.
		:return string of headings for output:
		"""
		# Subject ID
		h = 'PID,filename,'
		
		# Event Counts
		for e in self.evTypes:
			h += self._varMap[e].replace(",","+") + ','

		# Contingencies
		h += 'a,b,c,d,OCV'
		return h

	def ResultsTuple(self):
		"""
		For result output.
		Concatenates the contingencies, pids, filenames, OSV, and the values for A, B, C, D from the results
		of analysis
		:return a tuple of results:
		"""
		# Subject ID
		rt = self.pid + ',' + self.filename.split('/')[-1] + ','

		# Event Counts
		for e in self.evTypes:
			rt += str(self.eventCnt[e]) + ','

		# Contingencies
		# tokens used for OCV computation
		tok_a = float(self.contingencies["a"])
		tok_b = float(self.contingencies["b"])
		tok_c = float(self.contingencies["c"])
		tok_d = float(self.contingencies["d"])

		# OCV operant contingency value
		OCV = 0
		if (tok_a + tok_b) == 0 or (tok_c + tok_d) == 0:
			OCV = "undefined"
		else:
			OCV = (tok_a / (tok_a + tok_b)) - (tok_c / (tok_c + tok_d))

		rt += str(self.contingencies["a"]) + ',' + str(self.contingencies["b"]) + ',' + str(self.contingencies["c"]) + ',' + str(self.contingencies["d"]) + ',' + str(OCV)
		return rt
	
class SeqAnalysis:
	"""
	Handler class the sequence analysis class. Makes calls to complete sequence analysis.
	"""

	def __init__(self, seqData, out_results, stopper):
		"""
		Initializes sequence analysis object with seqData object, result output format, and stopper for signaling
		end of sequence analysis.

		:param seqData:
		:param out_results:
		:param stopper:
		"""

		# extract items from seqData object
		self.varMap = seqData.seq_config

		# prime for writing output
		batch_single = None
		if len(seqData.its_dict) > 1:
			batch_single = "Batch"
		else:
			batch_single = "Single"

		# setup vars
		self.results = []
		self.out_results = out_results
		self.error_results = []
		self.stopper = stopper
		self.tLock = threading.Lock()

		# kick off threads in batch
		while len(seqData.its_dict) > 0:
			# prep for run
			tempItem = {}
			tempDict = {}
			threads = []
			for i in range(seqData.num_threads):
				try:
					tempItem = seqData.its_dict.popitem()
					tempDict.update({tempItem[0]:tempItem[1]})
				except KeyError:
					pass # dict is empty
			
			# perform run
			for k,v in tempDict.iteritems():
				t = threading.Thread(target=self.Perform, args=(k,v,))
				t.daemon = True
				threads.append(t)
				t.start()

			# wait for threads
			for thread in threads:
				thread.join()

		if not stopper.is_set():
			# write output
			output_data = OutData(batch_single, seqData.seq_config,self.results)
			if '.xlsx' in seqData.output_format:
				output_xlsx(output_data)
			if '.csv' in seqData.output_format:
				output_csv(output_data)
			if '.txt' in seqData.output_format:
				ouput_txt(output_data)

			# report analysis result
			if len(self.error_results) > 0:
				self.out_results.append("Failed Sequence Analysis!")
				print 'self.error_results = ' + str(self.error_results)
			else:
				self.out_results.append("Successful Sequence Analysis!")


	def Perform(self, pID, path):
		"""
		Initiates organizing the data for analysis.
		Looks at the files in the path, and determines course of action for .its files or .csv files to prepare the
		xml parse tree or the data frame based on the input file type.
		It then calls the preceding methods to complete analysis.
		:param pID:
		:param path:
		:return:
		"""
		# retrieve work items from queue
		if not self.stopper.is_set():
			try:
				# Announce
				print 'Analysis in progress on pID=' + str(pID) + ', file=' + path

				# Define necessary objects
				eiList = None
				tree = None

				# INITIALIZE ESSENTIAL OBJECTS
				#Init event item list
				print '+++ Generating EItemList() ...'
				eiList = EItemList(_varMap=self.varMap, pid=pID, filename=path)
				print '+++ EItemList() created successfully.'
				
				if os.path.splitext(path)[1] == '.csv':
					print '+++ Processing .csv file ...'
					f = open(path,'r')
					rows = f.read().replace('\r','').split('\n')
					f.close()
					
					csv_data = []
					for i in range(1, len(rows)-1):
						csv_data.append( rows[i].split(',') )

					csv_arr = [csv_data[0][0], csv_data[0][1]] 
					print '+++ Created data: ' + str(csv_arr) + ' ...'

					eiList.AddEItemCSV(csv_arr, flag='Initial')
					
					print '+++ Iterating over rows of .csv file ...'
					for i in range(1, len(csv_data) - 1):
						csv_arr[0] = csv_data[i][0]
						csv_arr[1] = csv_data[i][1]
						eiList.AddEItemCSV(csv_arr)
					csv_arr[0] = csv_data[-1][0]
					csv_arr[1] = csv_data[-1][1]
					eiList.AddEItemCSV(csv_arr, flag='Terminal')

					#Insert contiguous pauses
					eiList.InsertPauses(CSV = True)
				else:
					#Load xml tree
					tree = ET.parse(path)

					#Get access to only the conversational segments in the .its file
					recNode = tree.find("ProcessingUnit")
					segs = list(recNode.iter("Segment"))

					# iterate over segments and copy
					eiList.AddEItem( segs[0], flag='Initial' )
					for i in range(1, len(segs)-1):
						eiList.AddEItem( segs[i] )
					eiList.AddEItem( segs[-1], flag='Terminal' )

					# free memory used by xml tree
					tree = None
					#Insert contiguous pauses
					eiList.InsertPauses(CSV = False)


				#Remove contiguous pauses
				if not(eiList.keepAllPauses):
					eiList.RemoveExtraneousPauses()

				#Tally each item in the EItemList
				print '+++ Counting items in EItemList ...'
				eiList.TallyItems()

				#Perform primary analysis
				print '+++ Performing sequential analysis ...'
				eiList.SeqAn()

				#write data and break from loop
				print '+++ Writing data ...'
				elh = eiList.Header()
				outputContent = ""
				with self.tLock:
					if len(self.results) == 0:
						self.results.append(elh)

				outputContent += eiList.ResultsTuple()

				# write data with Lock on results
				with self.tLock:
					self.results.append(outputContent)

			# Log All Errors
			except Exception as e:
				with self.tLock:
					self.error_results.append(str(e))
					
