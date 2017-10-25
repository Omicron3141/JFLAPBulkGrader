
# coding=utf-8

import xml.parsers.expat
import sys
from os.path import splitext

# 3 handler functions
def tm_start_element(name, attrs):
    global STATES, TYPES, current_state_id, seeking_start_state, \
           seeking_end_state, seeking_trans, seeking_read, seeking_write, \
           seeking_move
    if name == "block":
        string = attrs['id']
        state_placeholder = [int(s) for s in string.split() if s.isdigit()]
        STATES += state_placeholder
        current_state_id = state_placeholder[0]
    if name == "from":
        seeking_start_state = True
    if name == "to":
        seeking_end_state = True
    if name == "read":
        seeking_read = True
    if name == "write":
        seeking_write = True
    if name == "move":
        seeking_move = True
    if name == "initial":
        TYPES[current_state_id] = ["initial"]
    if name == "final":
        if TYPES.has_key(current_state_id):
            TYPES[current_state_id] += ["final"]
        else:
            TYPES[current_state_id] = ["final"]

def tm_end_element(name):
    pass

def tm_char_data(data):
    global TRANS, current_state_id, \
           current_start_state, current_end_state, \
           seeking_start_state, current_trans, seeking_trans, \
           seeking_end_state, current_read , seeking_read, \
           current_write, seeking_write, current_move, seeking_move
    data_without_space = data.strip()
    if len(data_without_space) > 0:
        pass

    if seeking_start_state:
        string = data_without_space
        state_placeholder = [int(s) for s in string.split() if s.isdigit()]
        current_start_state = state_placeholder[0]
        seeking_start_state = False

    if seeking_end_state:
        string = data_without_space
        state_placeholder = [int(s) for s in string.split() if s.isdigit()]
        current_end_state = state_placeholder[0]
        seeking_end_state = False

    if seeking_read:
        string = data_without_space
        state_placeholder = [s for s in string.split()]

        if len(state_placeholder)<1:
            state_placeholder = ['']
        current_read = state_placeholder[0]
        seeking_read = False

    if seeking_write:
        string = data_without_space
        state_placeholder = [s for s in string.split()]

        if len(state_placeholder)<1:
            state_placeholder = ['']
        current_write = state_placeholder[0]
        seeking_write = False

    if seeking_move:
        string = data_without_space
        state_placeholder = [s for s in string.split() if s.isalpha()]
        current_move = state_placeholder[0]

        if (current_start_state,current_end_state) in TRANS:
            TRANS[current_start_state,current_end_state] += [[current_read, current_write, current_move]]

        else:
            TRANS[current_start_state, current_end_state] = [[current_read, current_write, current_move]]
        seeking_move = False


def tm_TRANSprocessing():
    global TRANS, TRANS2
    TRANS2 = []
    for k in TRANS.iteritems():
        TRANS2.extend([k])

    for k in range(len(TRANS2)):
        trans_list = TRANS2[k][1]

        for j in range(len(trans_list)):
          if trans_list[j][0] == '': trans_list[j][0] = '*'

          if trans_list[j][1] == '': trans_list[j][1] = '*'

def tm_takingInput(filename):
    global INPUTS,INPUTS2
    INPUTS2 = {}
    f = open(filename)
    L = f.readlines()

    for line in L:
        line = line.strip()
        pieces = line.split()

        if len(pieces)==3:
            pieces = [pieces[0],pieces[2]]
        INPUTS.extend([pieces])

    for i in range(len(INPUTS)):

        if len(INPUTS[i]) == 0:
            INPUTS2[""] = True

        elif len(INPUTS[i]) == 1:
            if INPUTS[i][0] != 'reject':
                INPUTS2[INPUTS[i][0]] = True

            elif INPUTS[i][0] == 'reject':
                INPUTS2[""] = False

            else:
                print "ERROR", INPUTS[i]
        elif INPUTS[i][1]=='reject':
            INPUTS2[INPUTS[i][0]] = False

        else:
            print "ERROR", INPUTS[i]
            INPUTS2[INPUTS[i][0]] = 'UNDEFINED. ERROR'
    f.close()

def tm_stateTrans2(sState, left, right):
    global BEENTO
    global steps
    THRESHOLD = 900  # max # of steps...
    TOO_MANY = "Too many steps!"
    possibleTrans = []


    if (sState, left, right) in BEENTO: return "Infinite Loop!"
    BEENTO[ (sState, left, right) ] = True # remember this state!

    # extend the right side as far as we need...
    if len(right)<1: right = right + '*'
    if len(left)<1: left = '*' + left

    # KEY DEBUGGING LINE: the state of the TM each time...
    #print left, "(" + str(sState) + ")", right

    # off on the right side with only blanks...
    #

    if sState in TYPES and 'final' in TYPES[sState]:
        return True

    elif steps >= THRESHOLD:
        print "...",
        return TOO_MANY  # a string...

    elif steps < THRESHOLD:
        N = len(TRANS2)
        num_of_matching_transitions = 0
        for k in range(N):
            cur_trans = TRANS2[k]
            src, dst = cur_trans[0]
            cur_char = right[0]  # current character under the read head
            trans_list = cur_trans[1]

            if src != sState: continue # keep going!

            N2 = len( trans_list )
            for j in range(N2):
              cur_arrow = trans_list[j]
              cur_char_to_read = cur_arrow[0]
              cur_char_to_write = cur_arrow[1]
              cur_dir_to_move = cur_arrow[2]
              if cur_char == cur_char_to_read:
                num_of_matching_transitions += 1 # are there any matching transitions?
                steps += 1  # global for counting maximum number of steps
                rest_of_right = right[1:]

                if cur_dir_to_move == 'R':
                    s = tm_stateTrans2(dst,left+cur_char_to_write,rest_of_right)
                    if s in [True,TOO_MANY]: return s
                elif cur_dir_to_move == 'L':
                    s = tm_stateTrans2(dst,left[:-1],left[-1]+cur_char_to_write+rest_of_right)
                    if s in [True,TOO_MANY]: return s
                else:  # it's 'S' for "Stay put"
                    s = tm_stateTrans2(dst,left,cur_char_to_write+rest_of_right)
                    if s in [True,TOO_MANY]: return s

        if num_of_matching_transitions == 0:
            return False

    # not sure we should get here, but just in case...
    return False

# 3 handler functions
def start_element(name, attrs):
    global STATES, TYPES, current_state_id, seeking_start_state, \
           seeking_end_state, seeking_trans

    if name == "state":
        string = attrs['id']
        state_placeholder = [int(s) for s in string.split() if s.isdigit()]
        STATES += state_placeholder
        current_state_id = state_placeholder[0]

    if name == "from":
        seeking_start_state = True

    if name == "to":
        seeking_end_state = True

    if name == "read":
        seeking_trans = True

    if name == "initial":
        TYPES[current_state_id] = ["initial"]

    if name == "final":
        if TYPES.has_key(current_state_id):
            TYPES[current_state_id] += ["final"]

        else:
            TYPES[current_state_id] = ["final"]

def end_element(name):
    pass

def char_data(data):
    global TRANS, current_state_id, \
           current_start_state, current_end_state, \
           seeking_start_state, current_trans, seeking_trans, \
           seeking_end_state

    data_without_space = data.strip()
    if len(data_without_space) > 0:
        state_desc = "seeking_start_state"
        if seeking_end_state: state_desc = "seeking_end_state"

        if seeking_trans: state_desc = "seeking_trans"

        pass

    if seeking_start_state:
        string = data_without_space
        state_placeholder = [int(s) for s in string.split() if s.isdigit()]
        current_start_state = state_placeholder[0]
        seeking_start_state = False

    if seeking_end_state:
        string = data_without_space
        state_placeholder = [int(s) for s in string.split() if s.isdigit()]
        current_end_state = state_placeholder[0]
        seeking_end_state = False

    if seeking_trans:
        string = data_without_space
        if string.strip() == '':
          this_trans = 'X'

        else:
          s = string.strip()
          this_trans = str(s)


        if (current_start_state,current_end_state) not in TRANS:
            TRANS[current_start_state,current_end_state] = [this_trans]

        else:
            TRANS[current_start_state,current_end_state] += [this_trans]
        seeking_trans = False


def TRANSprocessing():
    global TRANS, TRANS2
    TRANS2 = []

    for k in TRANS.iteritems():
        TRANS2.extend([k])

def takingInput(filename):
    global INPUTS,INPUTS2
    INPUTS2 = {}
    f = open(filename)
    L = f.readlines()

    for line in L:
        line = line.strip()
        pieces = line.split()
        if len(pieces)==1:
            if not pieces[0].isdigit():
                pieces = ['','reject']
        if len(pieces)==0:
            pieces = ['']
        INPUTS.extend([pieces])
    for i in range(len(INPUTS)):
        if len(INPUTS[i])<2:
            INPUTS2[INPUTS[i][0]] = True
        else:
            INPUTS2[INPUTS[i][0]] = False
    f.close()

def stateTrans2(sState, inputstring):
    # BEENTO should store both the current state AND the inputstring.
    # so when it returns again, it'll def. be a loop.
    global BEENTO

    """
    print
    print "sState = ", sState
    print "inputstring = ", inputstring
    """

    if (inputstring,sState) in BEENTO:
      return False   # already been here!

    BEENTO[ (inputstring,sState) ] = True  # now we've been here!

    if len(inputstring) == 0:  # done!

        for k in range(len(TRANS2)):
            if TRANS2[k][0][0] == sState and TRANS2[k][1] == 'X':
                newState = TRANS2[k][0][1]

                if newState in TYPES and 'final' in TYPES[newState]:
                    return True

        if sState in TYPES and 'final' in TYPES[sState]:
            return True


    # handle the lambdas
    N = len(TRANS2)
    for k in range(N):
        cur_trans = TRANS2[k]
        src, dst = cur_trans[0]
        trans_chars = cur_trans[1]

        if src != sState: continue  # not the right start state

        if 'X' in trans_chars:
            s = stateTrans2(dst,inputstring)
            if s == True: return True

    if len(inputstring) > 0:
        next_char = inputstring[0]
        rest_of_input = inputstring[1:]

        N = len(TRANS2)
        for k in range(N):
            cur_trans = TRANS2[k]
            src, dst = cur_trans[0]
            trans_chars = cur_trans[1]

            if src != sState: continue  # not the right start state

            if next_char in trans_chars:
                s = stateTrans2(dst,rest_of_input)
                if s == True: return True

    return False


"""
Some directories and names...
"""

def currentRunTests(cmdPrefix, testFile, solution, timeLimit):
  #The students file is the basename of the test file with the jflap extension
  studentFile = splitext(testFile)[0] + '.jff'
  turing = False
  if "tm" in studentFile:
      turing = True
  print(turing)

  try:
    #
    # The code below is modified from the overall function (defined above)
    #

    global INPUTS, TRANS, STATES, TYPES, TRANS2, TRANS3, BEENTO, count, success, \
           current_state_id, current_start_state, current_end_state, seeking_start_state, \
           seeking_end_state, seeking_trans, current_trans, seeking_read, seeking_write, \
           seeking_move, steps
    #Resetting a bunch of globals. This is required to allow multiple test files
    #to be run in sequence
    STATES = []
    TYPES = {}
    TRANS = {}
    TRANS2 = []
    TRANS3 = []
    INPUTS = []
    BEENTO = {}
    count = 0
    current_state_id = None
    current_start_state = None
    current_end_state = None
    seeking_start_state = False
    seeking_end_state = False
    seeking_trans = False
    current_trans = None

    seeking_read = False
    current_read = None
    seeking_write = False
    current_write = None
    seeking_move = False
    current_move = None

    p = xml.parsers.expat.ParserCreate()

    if turing:
        p.StartElementHandler = tm_start_element
        p.EndElementHandler = tm_end_element
        p.CharacterDataHandler = tm_char_data
    
    else:
        p.StartElementHandler = start_element
        p.EndElementHandler = end_element
        p.CharacterDataHandler = char_data

    #Using with syntax to parse the student's file
    with open(studentFile) as f:
      p.ParseFile(f)

    #Don't know what this does the original was not documented

    if turing:
        tm_TRANSprocessing()
        tm_takingInput(solution)
    
    else:
        TRANSprocessing()

    #
    # We deviate from overall here so that we can handle the output the way we
    # want to provide data back to the caller. This code is based on checker
    #

        #Load the inputs
        takingInput(solution)

    #get the number of states
    num_states = len(STATES)

    #find the initial state
    initial_state = None
    for k in TYPES.keys():
      if 'initial' in TYPES[k]:
        initial_state = k

    if initial_state == None:
      #If we hav eno initial state just die
      summary = {}
      summary['numStates'] = num_states
      summary['died'] = True
      summary['rawErr'] = "Automaton is missing its initial state"
      summary['timeout'] = False
      return summary, {}

    summary = {}
    summary['numStates'] = num_states
    summary['rawout'] = ''
    summary['rawErr'] = ''
    summary['failedTests'] = 0
    summary['totalTests'] = 0
    summary['timeout'] = False
    summary['died'] = False
    failedTests = {}

    for i in INPUTS2.iterkeys():
        BEENTO = {}
        steps = 0
        if turing:
            result = tm_stateTrans2(initial_state, '', i)
        else:
            result = stateTrans2(initial_state,i)
        summary['totalTests'] += 1
        if INPUTS2[i] != result:
            summary['failedTests'] += 1

            #create a failure report
            report = {}
            report['hint'] = "Expected: " + str(INPUTS2[i]) + " Got: " + str(result)
            if i == '':
                failedTests['empty'] = report
            else:
                failedTests[i]  = report

    return summary, failedTests

  except Exception as e:
    #I don't know what errors the system can throw or how it throws them so I
    #will catch all errors and just report them rather than trying to be smartimport traceback
    import traceback
    tb = traceback.format_exc()
    summary = {}
    summary['died'] = True
    summary['rawErr'] = str(tb)
    summary['timeout'] = False
    return summary, {}

def runTests(cmdPrefix, testFile, solution, timeLimit = None):
    # Get the result dictionaries from both systems.
    print("[JFLAP] Calling into the current testing system...")
    currentSummary, currentFailedTests = currentRunTests(cmdPrefix, testFile, solution, timeLimit)

    # Get the total number of tests from both systems.
    if not currentSummary['died']:
        currentTotalTests = currentSummary["totalTests"]

    # Get the names of the failed tests from both systems.
    currentFailedTestNames = list(currentFailedTests)
    # Check if there is a substantial difference between the results
    # obtained by the two systems.

    # TODO(Radon): Replace these print statements with appropriate
    # logging calls.
    print("[JFLAP] --> Current tester")
    print("[JFLAP] summary = {}" .format(currentSummary))
    print("[JFLAP] failedTests = {}" .format(currentFailedTests))
    return currentSummary, currentFailedTests

if __name__ == "__main__":
    filename = sys.argv[1]
    solutions = sys.argv[2]
    runTests([], filename, solutions)