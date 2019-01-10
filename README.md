# SPR_Create_Dotmatics_ADLP_File
Project for processing SPR Data for upload to Dotmatics via ADLP

**Overview**

Takes SPR binding data and reformats the data into an Excel file for upload to Dotmatics through Broad's ADLP data upload portal.

## Environment Setup (Skip this section if done before)
__Follow the steps below for initial setup. If initial setup was conducted previously, skip to next section__.

_Take Note: The following procedure has been tested for Mac OS. Different commands are needed for Windows._

### Setup python on your computer and download script files

1. Create a github.com account by clicking the following link. This is free. (https://github.com)
    - This is necessary in order to copy all of the files needed to run the SPR to ADLP scripts.
    - Another advantage is any bugs or changes made can be easily synced to your local hard drive.
2. Download and Install Anaconda with Python version 3.7 for Mac by clicking link. (https://www.anaconda.com/download/#macos)
    - Anaconda is a distribution of software packages that are very useful for data science.
    - With the Anaconda download, python version 3 or greater will be automatically installed. Mac OS comes with version 2.7 but this is an older version that may cause issues.
3. Create a new file folder on your hard drive titled "PythonProjects" using the terminal.
    1. Open Terminal.
        - Hold command + space to bring up spotlight search. Type 'terminal' and press 'return'.
    2. In terminal, create a new folder on your hard drive titled "PythonProjects". 
        - Type or copy/paste command: __mkdir PycharmProjects__
        - Press 'return'
    3. In terminal navigate into "PythonProjects" by typing or copy/paste the command: __cd PythonProjects__
        - Press 'enter'
4. Fork this repo by clicking 'Fork' in the upper right corner of this webpage.
    - Forking means that all of the files necessary to run the SPR to ADLP scripts will be copied to your personal github account.
    - Later we will sync these files to your local hard drive in the PythonProjects folder you created above.
5. Once this repo is forked to your github account, navigate to the top project folder on github and click the green button 'Clone or download'. Next, click the button that looks like a clipboard to copy the link to your clipboard.
5. Navigate back to terminal.
6. Type command: __git clone 'paste contents of clipboard'__
7. Press 'return'
    - All the files needed should be copied to your local hard drive in the PythonProjects folder.
8. Navigate *into* the folder containing all of projects files. 
9. Type or copy/paste command: __cd SPR_Create_Dotmatics_ADLP_File__

### Create new Conda environment and install SPR to ADLP script dependencies.

 1. Navigate to terminal.
 2. Make sure you are in the SPR_Create_Dotmatics_ADLP_File file folder.
    - If your are not sure type command: cd ~
    - Press 'enter'
    - Type or copy/paste command: __cd PythonProjects__
    - Type or copy/paste command: __cd SPR_Create_Dotmatics_ADLP_File__
 3. Create and activate Conda Environment
    - Type or copy/paste command: __conda env create --file SRP_ADLP_env.txt__
    - Type or copy/paste command: __source activate SPR_ADLP_env__
    
## Create SPR setup file for dose response experiment

## Create ADLP upload file from Biacore dose response affinity experiment.

1. Create both affinity as well as kinetic analysis of the data in the SPR evaluation software.
2. Export both affinity as well as kinetic analysis.
    - Click on *affinity analysis* under 'Screening'
        - Right click on the sensorgram thumbnails and select 'Export All Graphs And Table'.
            - Save one Biacore hard drive.
      Click on *kinetic analysis* under 'Screening'.
        - Right click on the sensorgram thumbnails and select 'Export All Graphs And Table'
            - Save on Biacore hard drive.
3. Transfer both folders from 2. above to SPR image export folder on flynn. 
    - tdts_users/Informatics and computational research/SPR_Image_import/year_month
4. Navigate back the the Biacore evaluation software.
5. Export the 'Report Point Table'
    - Click on Report Point Table' under the Report Point Section.
    - Click File --> Export --> Results To Excel
    - Save this file either on flynn or on your hard drive.
6. Navigate to the following folder using finder: 
    - /Users/user_name/PythonProjects/SPR_Create_Dotmatics_ADLP_File/Example Files
    - Copy the Config.txt file to another location on your hard drive.
    - Open the Config.txt and replace all the paths as well as variables with those for your experiment.
    - __Trick:__ To copy file or folder paths, right click on the file or folder and hold the option key. Next, select Copy "File Name" as Pathname.
 
   
