#import os
import PySimpleGUI as gui
from programConstants import constants as const
from loguru import logger as log

#-----------------------------------------------             
#-----------------------------------------------
#-------------------- MENUS --------------------
#-----------------------------------------------
#-----------------------------------------------   

class SimplePopup:
    def __init__(self, message, popupTitle) -> None:
        gui.Popup(message, title=popupTitle)

class ContactsChoiceGUI:
    def __init__(self):
        self.event = None
        self.values = None
        self.horizontalSepLen = 35    
    
    def showUserTheGUI(self):
        layout = []
        topText = ["Choose from here", "The contacts"]
        for s in topText:
            layout.append([gui.Text(s, justification = 'left')])
        
        layout.append([gui.Input(), gui.FolderBrowse(initial_folder = self.previouslySelectedFolder)])
        bottomText = ["The file will get saved only when you press Finish"]
        for s in bottomText:
            layout.append([gui.Text(s, text_color = 'grey', justification = 'left')])        
        layout.append([gui.Text('_' * self.horizontalSepLen, justification = 'right', text_color = 'black')])
        layout.append([gui.Button(const.GlobalConstants.EVENT_CANCEL), gui.Button('Ok')])
        
        window = gui.Window('', layout, grab_anywhere = False, element_justification = 'right')    
        self.event, self.values = window.read()        
        window.close()
 
class FolderChoiceMenu:
    def __init__(self, fileOps):
        self.event = None
        self.values = None
        self.horizontalSepLen = 35    
        self.fileOps = fileOps  
        self.folderNameStorageFile = const.GlobalConstants.previouslySelectedFolderForDuplicatesCheck
        self.previouslySelectedFolder = None
    
    def showUserTheMenu(self, topText, bottomText):
        #---choose mode of running
        layout = []
        for s in topText:
            layout.append([gui.Text(s, justification = 'left')])
        self.checkForPreviouslySelectedFolder()
        layout.append([gui.Input(), gui.FolderBrowse(initial_folder = self.previouslySelectedFolder)])
        for s in bottomText:
            layout.append([gui.Text(s, text_color = 'grey', justification = 'left')])        
        layout.append([gui.Text('_' * self.horizontalSepLen, justification = 'right', text_color = 'black')])
        layout.append([gui.Button(const.GlobalConstants.EVENT_CANCEL), gui.Button('Ok')])
        
        window = gui.Window('', layout, grab_anywhere = False, element_justification = 'right')    
        self.event, self.values = window.read()        
        window.close()
    
    def getUserChoice(self):
        retVal = None
        if self.event == gui.WIN_CLOSED or self.event == const.GlobalConstants.EVENT_EXIT or self.event == const.GlobalConstants.EVENT_CANCEL or self.values[const.GlobalConstants.FIRST_POSITION_IN_LIST] == '':
            #retVal = FileSearchModes.choice_None
            log.info('Exiting')
            exit()
        else:
            folderChosen = self.values[const.GlobalConstants.FIRST_POSITION_IN_LIST]
            if self.fileOps.isThisValidDirectory(folderChosen):
                retVal = self.fileOps.folderSlash(folderChosen)
                self.setThisFolderAsThePreviouslySelectedFolder(retVal)
            else:
                retVal = const.FileSearchModes.choice_None
#         if retVal == FileSearchModes.choice_None:
#             gui.popup('Please select a valid folder next time. Exiting now.')
#             exit()    
        return retVal 
    
    def checkForPreviouslySelectedFolder(self):
        if self.fileOps.isValidFile(self.folderNameStorageFile):#there is a file storing the previously selected folder
            lines = self.fileOps.readFromFile(self.folderNameStorageFile)
            self.previouslySelectedFolder = lines[const.GlobalConstants.FIRST_POSITION_IN_LIST]
            if not self.fileOps.isThisValidDirectory(self.previouslySelectedFolder):
                self.previouslySelectedFolder = None
        else:
            self.previouslySelectedFolder = None
        if self.previouslySelectedFolder == None:
            self.previouslySelectedFolder = self.fileOps.getCurrentDirectory()
            self.setThisFolderAsThePreviouslySelectedFolder(self.previouslySelectedFolder)

    def setThisFolderAsThePreviouslySelectedFolder(self, folderName):
        nameAsList = [folderName] #need to convert to list, else the writing function will write each letter in a separate line
        self.fileOps.writeLinesToFile(self.folderNameStorageFile, nameAsList)

