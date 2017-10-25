import json
import re
import math
from jflapgrader_py2 import *
import sys
	
def runGrader(testFile, studentFile, maxPoints):
	dfa = False
	turing = False

	if "df" in testFile:
		dfa = True
	elif "tm" in testFile:
		turing = True
	
	studentFileName = studentFile

	summary, failedTests = runTests([], studentFile, testFile, None)


	

	if summary["died"]:
		score = 0
		output = summary["rawErr"]
	
	else:
		totalTests = summary['totalTests']
		numfailedTests = summary['failedTests']
		numcorrectTests = totalTests - numfailedTests
		
		thresh = math.ceil(totalTests*.8)
		maxPoints = int(maxPoints)
		threshScore = maxPoints*.8
		
		if numcorrectTests == totalTests:
			score = maxPoints
			if dfa:
				output = "DFA works for all test cases!"
			elif turing:
				output = "TM works for all test cases!"
			else:
				output = "NFA works for all test cases!"

		elif numcorrectTests < thresh:
			score = 0
			if dfa:
				output = "DFA failed too many test cases." + \
					 "\nHint: Check behavior by stepping through failed input."
			elif turing:
				output = "TM failed too many test cases." + \
					 "\nHint: Check behavior by stepping through failed input."
			else:
				output = "NFA failed too many test cases." + \
					 "\nHint: Check behavior by stepping through failed input."
			

		else:
			score = round((maxPoints*numcorrectTests*2.0)/totalTests)/2
			if dfa:
				output = "DFA passed most test cases." + \
					 "\nHint: Check behavior by stepping through failed input."
			elif turing:
				output = "TM passed most test cases." + \
					 "\nHint: Check behavior by stepping through failed input."
			else:
				output = "NFA passed most test cases." + \
					 "\nHint: Check behavior by stepping through failed input."


		# print "failed test is {}".format(  failedTests)
		for test in failedTests:
			output += "\nTest input {} failed.".format(test)

	#fill in result for test
	testResult = {
		'score':score,
		'max_score':maxPoints,
		'output':output,
	}
	return {"tests":[testResult]}




if __name__ == "__main__":
	studentFile = sys.argv[1]
	testFile = sys.argv[2]
	maxScore = sys.argv[3]
	testResults = runGrader(testFile, studentFile, maxScore)
	with open('results.json', 'w+') as outfile:
		json.dump(testResults, outfile, indent=4)
