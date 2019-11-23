import sys, os, shutil
import mutantLibFunctions as libFuncs

sectionBreak = "\n_____________________________________________________________________\n\n"
outputDirectory = "mutants"
mutantFileTemplate = outputDirectory + "/{}_mutant_{}_{}.{}"

#Function to mutate software according to provided arguments 
def mutateSoftware(origProgram, line, pos, mutant, mutantFormat):
    #Determine program name (e.g. "program") & extension (e.g. ".py")
    programComponents = origProgram.split(".")
    programName = programComponents[0]
    programExtension = programComponents[1]
    #Format mutated program name using original program name & mutant to be inserted
    mutantProgram = mutantFormat.format(programName, line, pos, programExtension)
    #Get original program code
    with open(origProgram, "r") as testProgram:
        mutantLines = testProgram.readlines()
    #Find the line where mutant is to be inserted & determine the line's code after mutation
    targetLine = mutantLines[line]
    mutatedLine = targetLine[0:pos] + mutant + targetLine[(pos+1):]
    #Reinsert the mutated line into the original program's code
    mutantLines[line] = mutatedLine
    #Save mutated program
    with open(mutantProgram, 'w+') as output:
        output.writelines(mutantLines)
    #Return name of mutant file generated
    return mutantProgram

#Determine if program called correctly & get command line arguments (mutant library)
if(len(sys.argv) != 2):
    print("\nThis program accepts 1 argument: \'Mutant Library Path\'")
    print("You entered {} arguments... Retry with 1 arguments!".format(len(sys.argv) - 1) + "\n")
    exit()
else:
    mutantLibName = sys.argv[1]
    #If the library cannot be found, exit the program
    if not os.path.isfile(mutantLibName):
        print("The mutant library {} does not exist... Retry with a valid mutant library!".format(mutantLibName))
        exit()

#Retrieve content of the mutant library
with open(mutantLibName, "r") as lib:
    libLines = lib.readlines()

#Create (remove first if necessary) directory to store mutant versions of SUT
if os.path.isdir(outputDirectory):
    shutil.rmtree(outputDirectory)
os.mkdir(outputDirectory)

#Parse data from the mutant library
sutName = libFuncs.getSoftwareUnderTest(libLines)
mutants = libFuncs.getLibMutants(0, libLines)

#Generate & store mutated versions of SUT
for mutant in mutants:
    mutantName = mutateSoftware(sutName, mutant["line"], mutant["position"], mutant["mutant"], mutantFileTemplate)
    libFuncs.addMutantFile(libLines, mutant, mutantName)

#Rewrite library to include mutant SUT file names
with open(mutantLibName, "w+") as lib:
    lib.writelines(libLines)

#Print out basic information to the user
print(sectionBreak)
print("This program inserts mutants (from a previously saved mutant library) into software under test:")
print("\t- Library of mutants: {}".format(mutantLibName))
print("\t- {} Mutants saved in directory: ./mutants".format(len(mutants)))
print(sectionBreak)