import sys, os, json
import mutantLibFunctions as libFunc
import multiprocessing as mp
import pandas as pd

mutantDirectory = "mutants"
mutantModuleTemplate = "{}_mutant_{}_{}"
softwareTemplate = "{}/{}.{}"
sectionBreak = "\n_____________________________________________________________________\n\n"
mutantCoverageTemplate = "Mutant Coverage:\n{} of {} mutants killed\t-\t{:.2%} Coverage\n\n"

#Function to find test vector that kills a mutant version of SUT
def killMutant(moduleName, mutant, original):
    #Import the mutant SUT module
    mutantSoftware = __import__(moduleName, globals=globals())
    #Compare input/output of the fault-free (original) & mutant versions of SUT
    for index, row in original.iterrows():
        #Select an input vector & its expected (fault-free) output
        testVector = row["args"]
        expectedOutput = row["output"]
        #Determine the mutant's output for the given input vector
        try:
            mutantOutput = mutantSoftware.main(testVector[0], testVector[1], testVector[2], testVector[3])
        except Exception as e:
            #If the input causes failure in the mutant software, store the input causing the fault & return
            mutant["killed"] = True
            mutant["test vector"] = testVector
            mutant["fault free output"] = expectedOutput
            mutant["mutant output"] = type(e) + ": " + e
            return mutant
        #If the output does not match the expected (fault-free) output, store the test data & the mutant has been 'killed'
        #Return as a single test vector that kills mutant is satifactory
        if mutantOutput != expectedOutput:
            mutant["killed"] = True
            mutant["test vector"] = testVector
            mutant["fault free output"] = expectedOutput
            mutant["mutant output"] = mutantOutput
            return mutant
    return None

#Ensure program has been called correctly
if(len(sys.argv) != 2):
    print("\nThis program accepts 1 argument: \'Mutant Library Path\'")
    print("You entered {} arguments... Retry with 1 argument!".format(len(sys.argv) - 1) + "\n")
    exit()
else:
    mutantLibName = sys.argv[1]
    #If the library cannot be found, exit the program
    if not os.path.isfile(mutantLibName):
        print("The mutant library {} does not exist... Retry with a valid mutant library!".format(mutantLibName))
        exit()

#Access the contents of the mutant library
with open(mutantLibName, "r") as mutantLib:
    libLines = mutantLib.readlines()

#Determine the name of the software under test
sutFileName = libFunc.getSoftwareUnderTest(libLines)
sutName = sutFileName.split(".")[0]
sutExtension = sutFileName.split(".")[1]

#Import the fault-free output of the software under test (SUT)
sut = __import__(sutName, globals=globals())

#Construct list of all test vectors (permutations of 4 values in argumentValues)
argumentValues = [-10.0, -1.0, -0.5, 0.5, 1.0, 10.0]
testVectors = [(arg1, arg2, arg3, arg4) for arg1 in argumentValues
                                       for arg2 in argumentValues
                                       for arg3 in argumentValues
                                       for arg4 in argumentValues]

#Save the fault-free input/output for all test vectors
faultFree = []
for vector in testVectors:
    arguments = (vector[0], vector[1], vector[2], vector[3])
    output = sut.main(vector[0], vector[1], vector[2], vector[3])
    faultFree.append([arguments, output])
faultFree = pd.DataFrame(faultFree, columns=["args", "output"])

#Determine the details of each mutant (line, position, original operation, mutant inserted)
mutants = libFunc.getLibMutants(1, libLines)

#Append mutant directory to path to access (import) mutant versions of SUT
sys.path.append(os.path.abspath(os.path.join(".", mutantDirectory)))

# Create a pool for multiprocessing
pool = mp.Pool(mp.cpu_count())

updatedMutants = []

#Determine the output of each mutated version
#If an input produces incorrect output, save test vector killing the mutant (see killMutant() above)
for mutant in mutants:
    mutantName = mutantModuleTemplate.format(sutName, mutant["line"], mutant["position"])
    # Start a new process to run a simulation
    updatedMutant = pool.apply_async(killMutant, args=(mutantName, mutant, faultFree), callback=(
        lambda updatedMutant: updatedMutants.append(updatedMutant)
    ))

# Wait for all simulations to complete before continuing
pool.close()
pool.join()

#Determine number of mutants killed by simulation
mutantsKilled = len(updatedMutants)

for mutant in updatedMutants:
    #Print information on mutants killed during simulation
    print("Mutant in {} killed by test vector: ({})".format(mutant["file"], ", ".join(str(arg) for arg in mutant['test vector'])))
    #Include data on whether mutant was killed, fault-free vs. mutant output, and the killing test vector in the library lines
    libFunc.addSimulationData(libLines, mutant)

#Print coverage statistics of mutant simulation
simulationCoverage = mutantCoverageTemplate.format(mutantsKilled, len(mutants), mutantsKilled/len(mutants))
print("\n" + simulationCoverage)

#Add simulation results (mutant coverage) to the library lines
libLines.append(sectionBreak)
libLines.append(simulationCoverage)

#Rewrite library to include simulation data & mutant coverage
with open(mutantLibName, "w+") as lib:
    lib.writelines(libLines)