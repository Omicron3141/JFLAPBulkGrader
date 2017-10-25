from grader import *
import re
import math
import sys
import os

if __name__ == "__main__":
	directory = sys.argv[1]
	testFile = sys.argv[2]
	maxScore = sys.argv[3]
	output = []
	for file in os.listdir(directory):
		path = os.path.join(directory, file)
		testResults = runGrader(testFile, path, maxScore)
		print testResults
		output.append((testResults['tests'][0]['score'], testResults['tests'][0]['output']))
	print output


