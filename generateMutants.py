import sys, os, random

targetOps = ["+", "-", "*", "/"]
sectionBreak = "\n_____________________________________________________________________\n\n"
mutantEntry = "Line: {} | Position: {} | Original: {} | Mutant: {}\n"
summaryFormat = "Mutant Summary: \n+ Mutants: {}\t- Mutants: {}\t* Mutants: {}\t/ Mutants: {}\n"
softwareUnderTest = "Software under test: {}"
 
def findOperations(line):
    #Ignore the line if empty 
    if not line: return None
    #Store position & type of all target operations in the line
    foundOps = []
    for position in range(len(line)):
        character = line[position]
        #If remainder of line is commented out, ignore possible mutations
        if character == "#": break
        #If a possible mutation is found, store its (position, operation)
        elif character in targetOps: foundOps.append((position, character))
    #Return None if no possible mutations found, else return the (position, operation) of all possible mutations
    if not foundOps: return None
    else: return foundOps

def chooseMutant(origOp, totals):
    #Copy target mutations so removal of an operation doesn't propagate
    possibleMutants = targetOps[:]
    possibleMutants.remove(origOp)
    #Randomly select the type of mutant to insert
    mutant = random.choice(possibleMutants)
    #Increment the # of mutants of this type generated (for summary)
    totals[mutant] += 1
    #Return the mutant operation to be injected in place of origOp
    return mutant

def addToLibrary(lib, line, pos, orig, mutant):
    #Format entry to reflect the mutant being added to the library
    libEntry = mutantEntry.format(line, pos, orig, mutant)
    #Write mutant entry to the mutant library
    lib.write(libEntry)

def summarizeLibrary(lib, totals):
    #Format summary with totals of each mutant type generated
    libSummary = summaryFormat.format(totals["+"], totals["-"], totals["*"], totals["/"])
    #Write section break & summary to the library
    lib.write(sectionBreak)
    lib.write(libSummary)

#Determine if program called correctly & get command line arguments (software under test, mutant library)
if(len(sys.argv) != 3):
    print("\nThis program accepts 2 arguments: \'Software Under Test\' \'Mutant Library Path\'")
    print("You entered {} arguments... Retry with 2 arguments!".format(len(sys.argv) - 1) + "\n")
    exit()
else:
    inputProgramPath = sys.argv[1]
    outputLibraryPath = sys.argv[2]
    #If the SUT cannot be found, exit the program
    if not os.path.isfile(inputProgramPath):
        print("The program {} does not exist... Retry with a valid program!".format(inputProgramPath))
        exit()

#Access content of software under test
with open(inputProgramPath, 'r') as program:
    programLines = program.readlines()

#Create & setup (headers, etc...) mutant library file
with open(outputLibraryPath, "w+") as lib:
    lib.write(softwareUnderTest.format(inputProgramPath))
    lib.write(sectionBreak)
    lib.write("Mutants:\n")

#Dictionary to store the # of each mutant type generated
mutantTotals = {"+": 0, "-": 0, "*": 0, "/": 0}

#Open the mutant library in append mode (do not change headers, etc...)
lib = open(outputLibraryPath, 'a')

for lineNum in range(len(programLines)):
    #Determine if SUT line can be mutated
    line = programLines[lineNum]
    opDetails = findOperations(line)
    if opDetails is None: continue

    #Add each possible mutation to the library
    for op in opDetails:
        opLoc = op[0]
        opType = op[1]
        #Determine the type of mutation to insert (and update totals for summary)
        newOp = chooseMutant(opType, mutantTotals)
        #Write the mutant details to the mutant library
        addToLibrary(lib, lineNum, opLoc, opType, newOp)

#Append the summary to the mutant library
summarizeLibrary(lib, mutantTotals)
lib.close()

#Print out basic information to the user
print(sectionBreak)
print("Mutants generated (and saved to the library of mutants) for a software under test:")
print("\t- " + softwareUnderTest.format(inputProgramPath))
print("\t- Mutant library saved at: {}".format(outputLibraryPath))
print(sectionBreak)