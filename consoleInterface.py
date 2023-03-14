import os
import PAMflourometryDataTransfom as dT


def takeYorN(inString):
    checkString = input(inString + " (y or n) \n")
    while (checkString not in ["Y", "y", "yes", "N", "n", "no"]):
        print("the answer must be either Y or N, or yes or no")
        checkString = input(inString)
    if (checkString in ["Y", "y", "yes"]):
        return True
    elif (checkString in ["N", "n", "no"]):
        return False
    else:
        return -1

def takeExistingDirectory(inString):
    checkString = input(inString + "\n")
    checkStringPath =  checkString
    #checkStringPath = os.path.abspath(checkStringPath)
    while (not os.path.exists(checkStringPath)):
        print(f"It appears that this filepath does not exist: " + checkStringPath)
        checkString = input(inString)
        #checkStringPath = os.path.abspath(checkString)
    return checkStringPath 

def getListFromInput(inString):
    strInput = -1
    outList = []
    while (strInput != "exit"):
        strInput = input(inString + " (write 'exit' to finish)\n")
        if (strInput != "exit"):
            outList.append(strInput)
    return outList

def main():
    print("""
    Welcome to the PAM data plotter and data collector. You will now be asked a few
    questions about how you want your data processed.
    """)
    
    makePlot = takeYorN("Do you want a plot of your data?")
    if makePlot:
        print("These are the possible columns to plot from: [t, ML, Temp., PAR, F, Fo\', Fm\', ~Fo\', Y(II), Y(NPQ), Y(NO), NPQ, qN, qP, qL, ETR, NPQown, PSII\'. rETR]")
        customAxes = takeYorN("Do you want to enter custom axes to plot? If not the defaults of 'NPQown' and 'rETR' are plotted against time 't'. ")
        if customAxes:
            data_on_x_axis = getListFromInput("What data do you want plotted on the x-axis. Write the exact name of the column(s) you want plotted on the x-axis.")
            print("This is what will be plotted on the x-axis: \n\t", data_on_x_axis)
            data_on_y_axis = getListFromInput("What data do you want plotted on the y-axis. Write the exact name of the column(s) you want plotted on the y-axis.")
            print("This is what will be plotted on the y-axis: \n\t", data_on_y_axis)

        listOfSampleNames = getListFromInput("Enter a common root of the samplenames you wish to be grouped. ex. ['LHCX1g1', 'LHCX1g2']")
        print("Samples containing these sections will be grouped: \n\t", listOfSampleNames)
        commonWTtag = input("Enter a common section of all wildtype samples. ex. 'WT' \n")
        # Add a question of what groupings you want for the data get list ["LHCX1", "LHCX2"]

    makeXLSX = takeYorN("Do you want your experiment data consolidated into an excel woorkbook (.xlsx)?")
    if makeXLSX:
        customXLSXname = takeYorN("Do you want a custom name for the xlsx file? the default is the name of your experiment data directory. ")
        if customXLSXname:
            ending = ".xlsx"
            xlsxFileName = input("What should the excel workbook file be named? \n")
            if xlsxFileName[-len(ending):] != ending:
                xlsxFileName += ending 
        
    makeCSV = takeYorN("Do you wish to have your data consolidated into .CSV files?")
    if makeCSV:
        customCSVname = takeYorN("Do you want a custom name for the .csv files? the default is the name of your experiment data directory + '_mainData.CSV', and '_maxData.CSV'. ")
        if customCSVname:
            ending = ".CSV"
            mainDataCSVFileName = input("What should the CSV file containing the main dataset be named? \n")
            if mainDataCSVFileName[-len(ending):] != ending:
                mainDataCSVFileName += ending
            maxDataCSVFileName = input("What should the CSV file containing the max values for each sample be named? \n")
            if maxDataCSVFileName[-len(ending):] != ending:
                maxDataCSVFileName += ending
    
    experimentDataDirectory = takeExistingDirectory("Write the directory where your PAM experimental data is stored. ex. '20210619'\n")

    if makePlot:
        if customAxes:
            dT.graphData(experimentDataDirectory, x_axis=data_on_x_axis, y_axis=data_on_y_axis, wildtypeTag=commonWTtag, sampleTags=listOfSampleNames)
        else:
            dT.graphData(experimentDataDirectory, wildtypeTag=commonWTtag, sampleTags=listOfSampleNames)
    
    if makeXLSX or makeCSV:
        if customXLSXname and customCSVname:
            dT.mergeData(experimentDataDirectory, saveXLSX=makeXLSX, saveCSV=makeCSV, excelFileName=xlsxFileName, csvFileNames=[mainDataCSVFileName, maxDataCSVFileName])
        elif (customXLSXname and not customCSVname):
            dT.mergeData(experimentDataDirectory, saveXLSX=makeXLSX, saveCSV=makeCSV, excelFileName=xlsxFileName)
        elif (not customXLSXname and customCSVname):
            dT.mergeData(experimentDataDirectory, saveXLSX=makeXLSX, saveCSV=makeCSV, csvFileNames=[mainDataCSVFileName, maxDataCSVFileName])
        else:
            dT.mergeData(experimentDataDirectory, saveXLSX=makeXLSX, saveCSV=makeCSV)

            
            
main()
