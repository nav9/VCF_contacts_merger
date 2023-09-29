'''
Virtual Contact File (VCF) merger
Created on 25-Sep-2023
@author: Navin
'''
import os
import sys
sys.dont_write_bytecode = True #Prevents the creation of some annoying cache files and folders. This line has to be present before all the other imports: https://docs.python.org/3/library/sys.html#sys.dont_write_bytecode and https://stackoverflow.com/a/71434629/453673 
from time import sleep
from fileAndFolder import fileFolderOperations
import PySimpleGUI as gui
from SimpleGUI import menus
from vcf_parser import VCF
from programConstants import constants as const
from loguru import logger as log
#log.add("logs.log", rotation="1 week")    # Once the file is too old, it's rotated
#logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
#log.remove() #removes the old handler which has DEBUG as the default log level
#log.add(sys.stdout, level="INFO") #add a new handler with INFO as the log level. You can also use

def main():#Reason for a main function https://stackoverflow.com/questions/60276536/why-do-we-put-a-main-function-in-python-instead-of-just-putting-the-code-direc    
    gui.theme('Dark grey 13')  
    fileOps = fileFolderOperations.FileOperations()
    #TODO: check if there's a temp file and allow user to continue from there

    # #---ask User where the VCF files are
    # topText = ['Which folder contains the VCF files? ']        
    # bottomText = ['Choose the folder containing all your VCF files. The program will merge', 'contacts to a new file and ask you about ambiguous contacts.', f'All subfolders will also be searched for {const.GlobalConstants.VCF_EXTENSION} files.']        
    # whichFolder = menus.FolderChoiceMenu(fileOps)
    # whichFolder.showUserTheMenu(topText, bottomText)
    # folderChosen = whichFolder.getUserChoice()
    folderChosen = '/home/nav/code/VCF_contacts_merger/sample_vcf' #TODO: remove this temporary override that was introduced for testing
    #folderChosen = '/home/nav/datasets' #TODO: remove this temporary override that was introduced for testing
    programStateFile = os.path.join(folderChosen, const.GlobalConstants.PROGRAM_STATE_SAVE_FILENAME)

    #---load all info from VCF files
    vcf_merger = None
    numDuplicates = 0
    #-check if an already saved program state is present, and whether the User would like to load from it    
    if fileOps.isValidFile(programStateFile):
        userChoice = menus.YesNoPopup("Found a previous program state. Load it?")
        if userChoice.getUserResponse():
            vcf_merger = loadProgramStateFromDisk(programStateFile, fileOps)
            numDuplicates = vcf_merger.getNumberOfDuplicates()
    if not vcf_merger:
        vcf_merger = VCF(fileOps, folderChosen)
        totalContacts, numDuplicates = vcf_merger.loadVCF(folderChosen) #loads and finds duplicates
        if totalContacts == 0:
            menus.SimplePopup(f"Either no VCF files were found in {folderChosen} or no recognizable contacts were present in them. Please check the folder/file(s)", "Error")
            exit()
        #---find indices of duplicates
        numDuplicates = vcf_merger.searchForDuplicateContactsBasedOnPhoneNumber()
        log.debug(f"Number of duplicates = {numDuplicates}")
    #---allow User to merge data via GUI if duplicates are found
    if numDuplicates == 0:
        vcf_merger.saveContactsToDisk()
        menus.SimplePopup(f"No duplicates found. Saved merged contacts to: {vcf_merger.getFolderUserChose()}{const.GlobalConstants.DEFAULT_SAVE_FILENAME}{const.GlobalConstants.VCF_EXTENSION}. Any old file with the same name is overwritten.\nContacts won't necessarily be in alphabetical order.", "Success")
    else:#create the GUI which allows User to examine the duplicates
        contactsUI = menus.ContactsChoiceGUI()   
        contactsUI.addBackendOfVCF(vcf_merger) #connect the backend to the GUI frontend
        contactsUI.createGUI()
        #---loop and check the GUI for events for as long as it's open
        while True:
            if contactsUI.checkIfNotClosedGUI(): 
                event, values = contactsUI.runEventLoop()
                if event == const.Layout.SAVE_BUTTON:
                    try:
                        saveProgramStateToDisk(vcf_merger, programStateFile, fileOps)
                    except Exception as e:
                        log.error(f"Unable to save program state to disk. Error is: {str(e)}")
                        menus.SimplePopup("Could not save program state to disk. This is nothing to worry about, as long as the merged contacts file is saved successfully.", "Minor error")
            else: 
                break #exit the program
            sleep(const.GlobalConstants.SLEEP_SECONDS) #relinquish program control to the operating system, for a while. Another (probably non-blocking) wait is located in simpleGUI.py, with the self.WINDOW_WAIT_TIMEOUT_MILLISECOND
    log.info("VCF merger program has ended its run. Thank you for trying/using it.")        

def saveProgramStateToDisk(vcf_merger, filenameWithPath, fileOps):
    fileOps.saveToPickleFile(vcf_merger, filenameWithPath)

def loadProgramStateFromDisk(filenameWithPath, fileOps):
    return fileOps.loadFromPickleFile(filenameWithPath)

if __name__ == '__main__':
    main()        
