# SPR_Create_Dotmatics_ADLP_File
Project for processing SPR Data for upload to Dotmatics via ADLP

**Overview**

Takes SPR binding data and reformats the data into an Excel file for upload to Dotmatics through Broad's ADLP data upload portal.

# Environment Setup 
__Follow the steps below for initial setup. If initial setup was conducted previously, skip to next section__.

_Take Note: The following procedure has been tested for Mac OS. Different commands are needed for Windows._

1. Create a github.com account by clicking the following link. This is free. (https://github.com)
    - This is necessary in order to copy all of the files needed to run the SPR to ADLP scripts.
    - Another advantage is any bugs or changes made can be easily synced to your local hard drive.
2. Download and Install Anaconda with Python version 3.7 for Mac by clicking link. (https://www.anaconda.com/download/#macos)
3. Create a new file folder on your hard drive titled "PythonProjects" using the terminal.
    1. Open Terminal.
        - Hold command + space to bring up spotlight search. Type 'terminal' and press return.
    2. In terminal, create a new folder on your hard drive titled "PythonProjects".
        - Type or copy/paste command: mkdir PycharmProjects
    3. In terminal navigate into "PythonProjects" by typing or copy/paste the command: cd PythonProjects
4. Fork this repo by clicking 'Fork' in the upper right corner of this webpage.
    - Forking means that all of the files necessary to run the SPR to ADLP scripts will be copied to your personal github account.
    - Later we will sync these files to your local hard drive in the PythonProjects folder you created above.
5. Once this repo is forked to your github account, navigate to the top project folder on github and click the green button 'Clone or download'. Next, click the button that looks like a clipboard to copy the link to your clipboard.
5. Navigate back to terminal.
6. Type command: git clone 'paste contents of clipboard'
    - All the files needed should be copied to your local hard drive in the PythonProjects folder.
 
   
