"""
The MIT License (MIT)
Copyright (c) 2016 Paul Yoder, Joshua Wade, Jon Tapp, Anne Warlaumont, and Amy Harbison

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from Automata import Automaton
import xml.etree.ElementTree as ET
from copy import deepcopy
import os

VERBOSE = True

# Event Item
class EItem:
	def __init__(self, attr):
		self.spkr = attr["spkr"]
		self.onset = attr["startTime"]
		self.offset = attr["endTime"]

	def GetFloatTime(self,arg='onset'):
		t = self.onset[2:-1] if arg=='onset' else self.offset[2:-1]
		return float(t)


# Event Item List
class EItemList:
	def __init__(self, _varMap={}, pid=0, its_filename=''):
		self.list = []
		self.list_ = []
		self._varMap = _varMap
		self.seqType = self._varMap["seqType"]
		self.pid = pid
		self.its_filename = its_filename
		self.relevantSpkrs = self._varMap["A"]+','+self._varMap["B"]+','+self._varMap["C"]+',Pause'
		self.pauseDur = float(self._varMap["PauseDur"])
		self.eventCnt = {"A":0,"B":0,"C":0,"P":0}
		self.evTypes = ["A","B","C","P"]
		self.contingencies = {"a":0, "b":0, "c":0, "d":0}
		self.round = True if "True" in self._varMap["roundingEnabled"] else False

	def AddEItem(self, seg, flag=None):
		# Specify CHN events as either CHNSP or CHNNSP events
		if 'CHN' in seg.attrib["spkr"]:
			seg.attrib["spkr"] = self.Modify_CHN_Events(seg)

		# Handle first and last events in .its file if they aren't relevant speakers
		if (flag is 'Initial' or flag is 'Terminal') and seg.attrib["spkr"] not in self.relevantSpkrs:
			seg.attrib["spkr"]="Pause"
		if seg.attrib["spkr"] in self.relevantSpkrs:
			self.list.append( EItem(seg.attrib) )

	def Modify_CHN_Events(self, seg):
		CHN_mod = ''
		if 'startUtt1' in seg.attrib:
			CHN_mod = 'CHNSP'
		else:
			CHN_mod = 'CHNNSP'
		return CHN_mod

	def Size(self):
		return len(self.list)

	def GetItem(self, index):
		return self.list[index]

	def InsertPauses(self):
		self.list_.append(deepcopy(self.list[0]))
		for i in range(1,self.Size()):
			#determine whether to add pause before copying event
			curEvT = self.list[i].GetFloatTime('onset')
			preEvT = self.list[i-1].GetFloatTime('offset')
			eT = curEvT - preEvT
			P = self.pauseDur
			if eT >= P:
				# calculate number of pauses to insert
				numP = 0
				if self.round is True:
					numP = int( (eT / P) + .5 )
				else:
					numP = int( (eT / float(P)) )
				for j in range(0,numP):
					# insert pause
					startTime = preEvT+(j*P)
					endTime = min(curEvT,startTime+P)
					pAttr = {"spkr":"Pause","startTime":str(startTime),"endTime":str(endTime)}
					self.list_.append( EItem(pAttr) )
			#add current event
			self.list_.append( deepcopy(self.list[i]) )

		#free memory used by interim list
		self.list = deepcopy(self.list_)
		self.list_ = None

	def TallyItems(self):
		for i in range(0, self.Size()): # iterate over Event Items
			for e in self.evTypes:			
				if self.list[i].spkr in self._varMap[e]:
					self.eventCnt[e] += 1

	def SeqAn(self):
		numItems = self.Size()
		# A-->B
		if self._varMap["seqType"] is 'A_B':
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
		elif self._varMap["seqType"] is 'AB_C':
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

	def Header(self):
		# Subject ID
		h = 'ID,its_filename,'
		
		# Event Counts
		for e in self.evTypes:
			h += self._varMap[e].replace(",","+") + ','

		# Contingencies
		h += 'a,b,c,d'
		return h

	def ResultsTuple(self):
		# Subject ID
		rt = self.pid + ','
		rt += self.its_filename.split('/')[-1] + ','

		# Event Counts
		for e in self.evTypes:
			rt += str(self.eventCnt[e]) + ','

		# Contingencies
		rt += str(self.contingencies["a"]) + ',' + str(self.contingencies["b"]) + ',' + str(self.contingencies["c"]) + ',' + str(self.contingencies["d"])
		return rt

class SAFSM(Automaton):
	def __init__(self):
		Automaton.__init__(self,VERBOSE)
		# Define States
		self.INIT = 0
		self.SCAN_COPY_XML = 1
		self.INSERT_PAUSES = 2
		self.TALLY_PASS = 3
		self.PRIMARY_ANALYSIS = 4
		self.WRITE_RESULTS = 5
		# Initial Transition
		self.Transition( self.INIT )

class SeqAnalysis:
	def __init__(self, _varMap={}, pID=None, fpaths=[]):
		self.pID=pID
		self.fpaths=fpaths
		self._varMap = _varMap
		for fpath in self.fpaths:
			self.Perform(fpath)

	def Perform(self, path):
		print 'Analysis in progress on pID=' + str(self.pID) + ', file=' + path
		# Init FSM object
		fsm = SAFSM()

		# Define necessary objects
		eiList = None
		tree = None

		# Begin Analysis loop
		while(True):
			# INITIALIZE ESSENTIAL OBJECTS
			if fsm.state_curr is fsm.INIT:
				#Init event item list
				eiList = EItemList(_varMap=self._varMap, pid=self.pID, its_filename=path)

				#Load xml tree
				tree = ET.parse(path)

				#enact transition to the next state
				fsm.Transition( fsm.SCAN_COPY_XML )

			# SCAN XML CONTENT AND COPY RELEVANT PORTIONS LOCALLY
			elif fsm.state_curr is fsm.SCAN_COPY_XML:
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
				
				#enact transition to the next state
				fsm.Transition( fsm.INSERT_PAUSES )

			# INSERT CONTIGUOUS PAUSES
			elif fsm.state_curr is fsm.INSERT_PAUSES:
				#Insert contiguous pauses
				eiList.InsertPauses()
				
				#enact transition to the next state
				fsm.Transition( fsm.TALLY_PASS )

			# PERFORM PASS OVER SEQUENCE AND TALLY EVENTS
			elif fsm.state_curr is fsm.TALLY_PASS:
				#Tally each item in the EItemList
				eiList.TallyItems()

				#enact transition to the next state
				fsm.Transition( fsm.PRIMARY_ANALYSIS )

			# PERFORM PRIMARY SEQUENTIAL ANSLYSIS
			elif fsm.state_curr is fsm.PRIMARY_ANALYSIS:
				#Perform primary analysis
				eiList.SeqAn()

				#enact transition to the next state
				fsm.Transition( fsm.WRITE_RESULTS )
	
			# WRITE ANALYSIS RESULTS TO OUTPUT CONTENT
			elif fsm.state_curr is fsm.WRITE_RESULTS:
				#write data and break from loop
				elh = eiList.Header()
				outputContent = ""
				if self._varMap["outputContent"] is "":
					outputContent = elh
				outputContent += '\n' + eiList.ResultsTuple()
				self._varMap["outputContent"] += outputContent
				break

	
