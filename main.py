'''
Virtual Contact File (VCF) merger
Created on 25-Sep-2023
@author: Navin
'''

import sys
sys.dont_write_bytecode = True #Prevents the creation of some annoying cache files and folders. This line has to be present before all the other imports: https://docs.python.org/3/library/sys.html#sys.dont_write_bytecode and https://stackoverflow.com/a/71434629/453673 
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

if __name__ == '__main__':
    gui.theme('Dark grey 13')  
    fileOps = fileFolderOperations.FileOperations()

    # #---ask User where the VCF files are
    # topText = ['Which folder contains the VCF files? ']        
    # bottomText = ['Choose the folder containing all your VCF files. The program will merge', 'contacts to a new file and ask you about ambiguous contacts.', f'All subfolders will also be searched for {const.GlobalConstants.VCF_EXTENSION} files.']        
    # whichFolder = menus.FolderChoiceMenu(fileOps)
    # whichFolder.showUserTheMenu(topText, bottomText)
    # folderChosen = whichFolder.getUserChoice()
    folderChosen = '/home/nav/code/VCF_contacts_merger/sample_vcf' #TODO: remove this temporary override
    
    #---load all info from VCF files
    vcf_merger = VCF(fileOps)
    vcf_merger.loadVCF(folderChosen)
    #---begin searching all VCF files for duplicates

