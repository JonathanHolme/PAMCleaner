import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from tailer import tail
from io import StringIO

def getCSVfilesList(experimentID, filesIdentifier = ").CSV"):
    """This function gets the experimentID directory, and returns a filtered pandas 
     Series based on the provided filesIdentifier.

    Args:
        experimentID (str, optional): the name of the directory(folder) where your experiment files are kept.
        filesIdentifier (str, optional): A identifiable string present in your folder that identifies your dataset. Defaults to ").CSV".

    Returns:
        pandas Series: A series containg the name of all selected
        string: A string declaring the path of the experiment files
    """
    # Generate the relative path location to the experimentID folder
    experimentPath = "./" + experimentID + "/"
    # Get a list of all files/elements in the directory
    filesList = os.listdir(experimentPath)
    # Filter out wanted files based on if their names contain the identifies string.
    fileNamesSeries = pd.Series([file for file in filesList if filesIdentifier in file])
    return fileNamesSeries, experimentPath

def extractLocalExperimentID(fileName, experimentID, sep= ","):
    with open(f"./{experimentID}/{fileName}", "r") as f:
        frame_names = f.readline()
    local_ID_list = frame_names.strip("\n").split(sep)
    return local_ID_list

def generateStrippedDataset(fileName, experimentID):
    """Create a pandas dataframe with only experimental data.

    Args:
        fileName (str): Name of the experiment's .csv file
        experimentID (str): Name of the experiment folder

    Returns:
        pandas DataFrame: pandas DataFrame containing the PAM experiment data.
    """
    # Read the experiment file .csv into a pandas dataframe  
    dataPAM_df = pd.read_csv(f"./{experimentID}/{fileName}", delimiter=";", skiprows=[0,2,3,4,5], skipfooter=1, engine="python")
    # Drop the first 3 rows as they do not contain experiment data
    #dataPAM_df = dataPAM_df.drop([0,1,2], axis=0)
    # Drop the last row as it doesn't contain experimantal data
    #dataPAM_df = dataPAM_df.iloc[:-1, :]
    # Remove all empty columns (columns containing NaN)
    dataPAM_df = dataPAM_df.dropna(axis=1)
    # Reset the row indexes of the dataframe (start at 0, 1, 2 ...) 
    dataPAM_df = dataPAM_df.reset_index()
    
    return dataPAM_df

def calculateValuesAndInject(PAMdata_df, local_ID_list):
    """Takes in a dataframe of PAM fluorometry data and calculates NPQown, PSII\',
    qP, and rETR. Returns a dataframe containing the calculated values along with 
    the original data. 

    Args:
        PAMdata_df (pandas DataFrame): A pandas Dataframe containing the PAM fluorometry data.

    Returns:
        pandas DataFrame: A pandas DataFrame containing the original data along with: NPQown, PSII\', qP, and rETR.   
        pandas Series: A pandas Series containing the maximal valuse in the Dataframe for: Fm, NPQ, Fo, and PSII.
    """
    # Find max Fm
    max_Fm = PAMdata_df["Fm'"].max()
    # Calculate NPQown maxFm/Fm'-1 and place it in a new column "NPQown"
    PAMdata_df['NPQown'] = (max_Fm/PAMdata_df["Fm\'"])-1
    # Find max NPQ
    max_NPQ = PAMdata_df["NPQown"].max()
    # Find max Fo
    max_Fo = PAMdata_df["~Fo'"].max()
    # Calculate phi PSIImax
    max_PSII = ((max_Fm - max_Fo)/max_Fm)
    # Calculate phi PSII' and place it in new column "PSII\'"
    PAMdata_df['PSII\''] = ((PAMdata_df["Fm\'"] - max_Fo)/PAMdata_df["Fm\'"])
    # Calculate qP 
    PAMdata_df['qP'] = ((PAMdata_df["Fm\'"] - max_Fm) / (PAMdata_df["Fm\'"] - max_Fo))
    # Calculate rETR = PSII*PAR
    PAMdata_df['rETR'] = PAMdata_df['PSII\''] * PAMdata_df['PAR']
    # Create a series of max values
    maxValues_Series = pd.Series([max_Fm, max_NPQ, max_Fo, max_PSII], index=["max_Fm", "max_NPQ", "max_Fo", "max_PSII"], name=", ".join(local_ID_list))

    return PAMdata_df, maxValues_Series

def accessAxes(ax, x_axes, y_axes, x, y):
    """ This function returns the axes (subplot) indicated by the x and y coordinates of a plot.

    Args:
        ax (matplotlib axis object): the axis/numpy array of axes (subplots) that we wish to access the axis of.  
        x_axes (list of strings): a list of names for values which should be plotted on the x_axes of the plot.
        y_axes (list of strings): a list of names for values which should be plotted on the y_axes of the plot.
        x (integer): The index for the row for the axis (subplot) which is to be accessed. 
        y (integer): The index for the column for the axis (subplot) which is to be accessed.

    Returns:
        ax (matplotlib axis object): the accessed axes object (subplot) denoted by the x (row) and y (column) indexes.
    """
    # If the axis object passed in is a numpy array (it has multiple subplots which must be further accessed).
    if type(ax) == type(np.array(0)):    
        # get the dimensionality of the subplots i.e. 1D or 2D array
        dimensions = ax.ndim
        # if the dimasionality of the subplots is 1D access the wanted subplot using a single accesser "[]"
        if (dimensions == 1):
            # if the list of x_axes is longer than one that is the "direction" which the array stretches so access with x
            if (len(x_axes) > 1):
                return ax[x]
            # if the list of y_axes is longer than one that is the "direction" which the array stretches so access with y
            elif (len(y_axes) > 1):
                return ax[y]
        # if the dimasionality of the plot is 2D, access the correct subplot by using both x and y to access the correct subplot
        elif (dimensions >= 2):
            return ax[x][y]
    # if the passed in ax object is not a numpy array, it is a single subplot (i.e. subplots == subplot) so we return the axis/subplot
    else:
        return ax


def plotPAMdata(PAMdata_df, local_ID_list, mpl_ax=None, x_axis = ["t"], y_axis = ["NPQown", "rETR"], plotDimensions = (7, 2), wildtypeTag = "WT", sampleTags = ["LHCX1g1", "LHCX1g2"], legendList=[]):
    """Takes in a dataframe of PAM fluorometry data and calculates and creates plots based on
    the wanted axes in x_axis and y_axis. The function returns the plot.

    Args:
        PAMdata_df (pandas DataFrame): A pandas Dataframe containing processed PAM fluorometry data.
        local_ID_list (list of strings): A list containing the local names/IDs of the samples.
        fig (matplotlib figure object): A figure the data from the dataframe will be plotted onto if provided. If not the function makes a new figure. Defaults to None.
        x_axis (list of strings): A list of which columns of data from the dataframe should be plotted on the x-axis. Defaults to ["t"]
        y_axis (list of strings): A list of which columns of data from the dataframe should be plotted on the y-axis. Defaults to ["NPQown", "rETR"]
        plotDImensions (tuple of ints): A tuple which dedicates how large each plot should be in the respective x- and y-axis. Defaults to (7, 5)
        wildtypeTag (string): A part of each WT sample name which allows them to be grouped while plotting. Defaults to "WT"
        sampleTags (list of strings): A part of each sample name to uniquely identify which samples should be grouped. Defaults to ["LHCX1g1", "LHCX1g2"]
        legendList (list of axis objects): A list used to hand axes between instances of plotPAMData to later construct a propper label for the plot containing all data.


    Returns:
        ax (matplotlib axis): A matplotlib figure axis containing created axis subplots.
        legendList (list of axis objects): A list used to hand axes between instances of plotPAMData to later construct a propper label for the plot containing all data.
    """
    
    # If no figure is provided make a new figure
    if (mpl_ax is None):
        fig, ax = plt.subplots(len(x_axis), len(y_axis), figsize=(len(x_axis)*plotDimensions[0], len(y_axis)*plotDimensions[1])) 
    else:
        ax = mpl_ax
    # For all x-axes
    for i in range(len(x_axis)):
        # Define x axis values as dexcribed in x_axis from the PAM fluorometry results DataFrame
        x = PAMdata_df[x_axis[i]]
        # For all y axes
        for j in range(len(y_axis)):
            # Define x axis values as dexcribed in x_axis from the PAM fluorometry results DataFrame            
            y = PAMdata_df[y_axis[j]]
            # Make an integer which keeps track of which color should be plotted for each graph
            colorInt = 0
            # List of iteratable colors for plots
            colorList = ['blue', 'red', 'green', 'magenta', 'yellow', 'blacl', 'white']
            
            # Gains access to the axes (the subfigures) and sets the x and y axis labels based on the labels given in x_axis and y_axis
            accessAxes(ax, x_axis, y_axis, i, j).set_xlabel(x_axis[i])
            accessAxes(ax, x_axis, y_axis, i, j).set_ylabel(y_axis[j])

            # Set a variable to be true if the current file has a local ID which contains the "Wildtype tag" which can be f.ex. "WT"
            wtTagInSampleSeries = any(wildtypeTag in string for string in local_ID_list)
            # If the local ID contains the wildtype tag the following is run
            if wtTagInSampleSeries:
                # On the current axis (subplot) plot the data 
                legendLine, = accessAxes(ax, x_axis, y_axis, i, j).plot(x, y, label = wildtypeTag, color="cyan")
                # Append a legend to the inputted legendlist (this can outside this function be used to plot a fully anotated figure with all datasources)
                legendList.append(legendLine)
            # Set a variable to be true if the current file has a local ID which contains the any of the "grouping tags" given in the sampleTag list which can be f.ex. ["LHCX1g1", "LHCX1g2"]
            for sampleTag in sampleTags:
                substringInList = any(sampleTag in string for string in local_ID_list)
                if substringInList:
                    # On the current axis (subplot) plot the data
                    legendLine, = accessAxes(ax, x_axis, y_axis, i, j).plot(x, y, label = sampleTag, color = colorList[colorInt])
                    # Append a legend to the inputted legendlist (this can outside this function be used to plot a fully anotated figure with all datasources)
                    legendList.append(legendLine)
                # Increment the colorInt which means that the color for each sample will be unique (up to 7 different)
                colorInt += 1
            
    # If no matplotlib axis was sendt into the function make a legend and the plot right away
    if (mpl_ax is None):
        ###Place a legend to the right of this smaller subplot.
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        #Show the plot
        plt.show()

    return ax, legendList

def writeXLSXfile(filepath, list_of_frames, sheet_names_list):
    """This function takes in a filepath and based on a list of pandas dataframes and a list of sheet names
    for which worksheet the dataframes should be saved creates a .xlsx from the pandaframes.

    Args:
        filepath (string): a filepath describing where the .xslx file should be created.
        list_of_frames (list of pandas dataFrames): The list of dataframes which should be saved to a .xlsx file.
        sheet_names_list (list of strings): The list of names for the sheets where the respective dataframes should be saved. 
    """
    if (len(list_of_frames) != len(sheet_names_list)):
        print("Error: the list of sheet names must be as long as the list of pandas dataframes")
        return 0
    with pd.ExcelWriter(filepath, mode="w") as writer:
        for i, dataFrame in enumerate(list_of_frames):
            dataFrame.to_excel(writer, sheet_name=sheet_names_list[i])

def createDirectoryIfNotPresent(directoryPath):
    """This function takes in a filepath, and if that filepath doesn't lead to a directory creates a directory there.

    Args:
        directoryPath (string): the path where the new directory should be created.
    """
    if not os.path.exists(directoryPath):
        os.makedirs(directoryPath)

def graphData(experimentID, mpl_ax=None, x_axis = ["t"], y_axis = ["NPQown", "rETR"], plotDimensions = (7, 2), wildtypeTag = "WT", sampleTags = ["LHCX1g1", "LHCX1g2"]):
    """This function assembles the plot from all the files in the experiment directory.

    Args:
        experimentID (string): The path/folder/directory name of the directory where your PAM data is stored. (must be in the same directory as the program).
        mpl_ax (axis object from matplotlib, optional): A preexisting plot the data from this run should be added to. Defaults to None.
        x_axis (list of strings, optional): The column headers which should be plotted along the x-axes. Defaults to ["t"].
        y_axis (list of strings, optional): The column headers which should be plotted along the y-axes. Defaults to ["NPQown", "rETR"].
        plotDimensions (tuple, optional): a size for the subplots (does not work!!!). Defaults to (7, 2).
        wildtypeTag (string, optional): A string describing which samples based on local ID should be classified as wildtype when plotted. Defaults to "WT".
        sampleTags (list of strings, optional): A list describing which samples based on local ID should be classified as diffrent samples when plotted. Defaults to ["LHCX1g1", "LHCX1g2"].
    """
    if (mpl_ax == None):
        fig, ax = plt.subplots()
    else:
        ax = mpl_ax
    fileNamesSeries, experimentPath = getCSVfilesList(experimentID)

    # Create an empty figure
    fig, ax = plt.subplots(len(x_axis), len(y_axis), figsize=(len(x_axis)*plotDimensions[0], len(y_axis)*plotDimensions[1]))


    legendList = []

    for fileName in fileNamesSeries:
        
        listOfSampleNames = extractLocalExperimentID(fileName, experimentID)

        strippedPAMdata_df = generateStrippedDataset(fileName, experimentID)

        calculatedPAMdata_df, calculatedValuesSeries = calculateValuesAndInject(strippedPAMdata_df, listOfSampleNames)
        
        ax, legendList = plotPAMdata(calculatedPAMdata_df, listOfSampleNames, mpl_ax=ax, x_axis=x_axis, y_axis=y_axis, plotDimensions=plotDimensions, wildtypeTag=wildtypeTag, sampleTags=sampleTags, legendList=legendList)

    labelSet = set()
    axisUniqueList = []
    for axis in legendList:
        if axis._label not in labelSet:
            axisUniqueList.append(axis)
            labelSet.add(axis._label)
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., handles=axisUniqueList)
    plt.show()


def mergeData(experimentID, saveXLSX, saveCSV, excelFileName=None, csvFileNames = [None, None]):
    """ This function takes in the experiment ID (i.e. the name of the folder/directory containing your data)
    and based on the truthiness of saveXLSX and saveCSV saves the data from your PAM fluorometry experiment into 
    a large .xlsx and two .CSV files respectively.

    Args:
        experimentID (string): The path/folder/directory name of the directory where your PAM data is stored. (must be in the same directory as the program).
        saveXLSX (bool): If True it saves the data into an .xlsx file.
        saveCSV (bool): If True it saves the data into two .csv files.
        excelFileName (string, optional): Is the name you want to give your merged data .xlsx file. Defaults to None.
        csvFileNames (list of strings, optional): Is a list of names for the main data .CSV followed by the name of the maximal values data .CSV file. Defaults to [None, None].

    Returns:
        This function returns nothing.
    """
    # If the pandas dataframes should be saved run the following 
    if saveXLSX or saveCSV:
        # Create the dataframes where data will be consolidated
        mainOut_df = pd.DataFrame()
        calcValuesOut = pd.DataFrame(columns=["max_Fm", "max_NPQ", "max_Fo", "max_PSII"])
    else:
        #if the function has been called while no data should be saved retrun -1 and exit
        return -1
    
    # Get a list of all files within the experiments directory. defaults to .csv files with the ";" delimiter and ending with ").csv"
    filesNameSeries, experimentPath = getCSVfilesList(experimentID)

    for fileName in filesNameSeries:
        # Get all sample names associated with each run, delimited by ",". load the data into a pandas Dataframe.
        listOfSampleNames = extractLocalExperimentID(fileName, experimentID)

        # Remove the upper 3 and lower 1 row of the .csv file as they do not contain experiment data
        strippedPAMdata_df = generateStrippedDataset(fileName, experimentID)
        # Calculate the NPQown, PSII', qP, and rETR values, and insert them into the dataframe. Also get max values for Fm, NPQ, Fo, and PSII which is then placed into a pandas Series.
        calculatedPAMdata_df, calculatedValuesSeries = calculateValuesAndInject(strippedPAMdata_df, listOfSampleNames)
        
        # Main Data
        # Add a column to the dataset which holds the sample names related to that data 
        calculatedPAMdata_df["sampleName"] = ", ".join(listOfSampleNames)
        # Merge the data for the current sample with the dataframe which holds all experimental data.
        mainOut_df = pd.concat([mainOut_df, calculatedPAMdata_df])

        # Max values
        # make the Series into a DataFrame with max values along the columns, and row name equal to the sample 
        calculatedValuesFrame = calculatedValuesSeries.to_frame().swapaxes(0,1)
        # Merge the max values for the current sample with the dataframe which holds all max values for all samples. 
        calcValuesOut = pd.concat([calcValuesOut, calculatedValuesFrame])
        
        
    # Rearrange the columns so the sample name column is the first column
    # Get the columns of the dataframe as a list
    df_cols = list(mainOut_df)
    # Delete the "sampleName" entry in the list and add it to the front
    df_cols.insert(0, df_cols.pop(df_cols.index("sampleName")))
    # Rearrange the columns of the dataframe according to the list
    mainOut_df = mainOut_df.loc[:, df_cols]
    # Reset the row indexes
    mainOut_df = mainOut_df.reset_index()

    # Create results directory
    results_directory = "myPAMresults"
    createDirectoryIfNotPresent(f"./{results_directory}")
    # Set the name of the excel file if none are given
    if excelFileName == None:
        excelFileName = f"{experimentID}.xlsx"

    # Save as excel file if saveXLSX is true
    if saveXLSX:
        writeXLSXfile(f"./{results_directory}/{excelFileName}", [mainOut_df, calcValuesOut], ["mainData", "maxValues"])
    
    # Set names for .csv files if none are given
    if (csvFileNames[0] == None):
        csvFileNames[0] = f"{experimentID}_mainData.CSV"
    if (csvFileNames[1] == None):
        csvFileNames[1] = f"{experimentID}_maxData.CSV"

    # Save as .csv files if saveCSV is true
    if saveCSV:
        mainOut_df.to_csv(f"./{results_directory}/{csvFileNames[0]}")
        calcValuesOut.to_csv(f"./{results_directory}/{csvFileNames[1]}")

exp_ID = "20230314"

csv_list = getCSVfilesList(exp_ID)[0]
print(csv_list[0])
df_strip_dataset = generateStrippedDataset(csv_list[0], exp_ID)
print(df_strip_dataset)
df_strip_dataset, max_values_series = calculateValuesAndInject(df_strip_dataset, csv_list)
print(df_strip_dataset)