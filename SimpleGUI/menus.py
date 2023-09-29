import textwrap
import PySimpleGUI as gui
from collections import namedtuple
from programConstants import constants as const
from loguru import logger as log
             
#-----------------------------------------------
#-------------------- MENUS --------------------
#-----------------------------------------------

class SimplePopup:
    def __init__(self, message, popupTitle) -> None:
        gui.popup_ok(message, title=popupTitle)

class YesNoPopup:
    def __init__(self) -> None:
        pass

    def getUserResponse(self, message, popupTitle):
        """ returns True if user chooses Yes. Else, returns False """
        userChoice = gui.popup_yes_no(message, title=popupTitle)
        return userChoice == const.Layout.YES_BUTTON

class ContactsChoiceGUI:
    def __init__(self):
        self.event = None
        self.values = None
        self.horizontalSepLen = 90    
        self.multilineTextboxWidth = 40
        self.multilineTextboxHeight = 20
        self.multilineWrapLength = 47
        self.layout = []
        self.backend = None
        self.window = None
        self.programRunning = True
        self.duplicateIndexAtGUI = None
        self.numDuplicates = None
        self.firstTimeClickingNextPrev = True
    
    def addBackendOfVCF(self, backendRef):
        self.backend = backendRef

    def createGUI(self):
        totalContacts = self.backend.getNumberOfContacts()
        self.numDuplicates = self.backend.getNumberOfDuplicates()        
        numFiles = len(self.backend.whichFilesWereConsideredVCF())
        self.layout.append([gui.Button(const.Layout.EXPLANATION_BUTTON, key = const.Layout.EXPLANATION_BUTTON)])
        topText = [f"{numFiles} {const.GlobalConstants.VCF_EXTENSION} files considered. The program has {totalContacts} contacts in memory, of which {self.numDuplicates} appear to have duplicates."]        
        for s in topText:
            self.layout.append([gui.Text(s, text_color = const.Layout.COLOR_GREY, justification = const.Layout.LEFT_JUSTIFY)])    
        self.layout.append([gui.Text('_' * self.horizontalSepLen, justification = const.Layout.RIGHT_JUSTIFY, text_color = const.Layout.COLOR_GREY)])
        contactColumnTitle = gui.Text("Contact(s) that will be saved")
        contactsColumnDefaultText = textwrap.fill(f"Select contacts by dragging the mouse pointer and cut / copy / paste using the usual Ctrl+x / Ctrl+c / Ctrl+v. Contacts in this column will be saved to disk when you click the {const.Layout.SAVE_BUTTON} button.", self.multilineWrapLength)
        contactsColumnDefaultText += "\n\n" + textwrap.fill(f"Start examining the contacts by clicking the {const.Layout.NEXT_BUTTON} button below", self.multilineWrapLength)
        contactsDisplay = gui.Multiline(contactsColumnDefaultText, size = (self.multilineTextboxWidth, self.multilineTextboxHeight), key = const.Layout.CONTACTS_DISPLAY_TEXTFIELD, horizontal_scroll = True, do_not_clear = True)        
        duplicatesColumnTitle = gui.Text("Duplicates")
        duplicatesColumnDefaultText = textwrap.fill(f"This column will display the assumed duplicates of the contact(s) shown in the other column. Any text in this 'Duplicates' column will not be saved to disk.", self.multilineWrapLength)
        duplicatesColumnDefaultText += "\n\n" + textwrap.fill(f"The program has {totalContacts} contacts in memory, of which {self.numDuplicates} appear to have duplicates.", self.multilineWrapLength)
        duplicatesDisplay = gui.Multiline(duplicatesColumnDefaultText, size = (self.multilineTextboxWidth, self.multilineTextboxHeight), key = const.Layout.DUPLICATES_DISPLAY_TEXTFIELD, horizontal_scroll = True, do_not_clear = True)
        leftColumn = [[duplicatesColumnTitle], [duplicatesDisplay]]
        rightColumn = [[contactColumnTitle], [contactsDisplay]]
        self.layout.append([gui.Column(leftColumn), gui.Column(rightColumn)])
        self.layout.append([gui.Button(const.Layout.PREV_BUTTON, key = const.Layout.PREV_BUTTON), 
                            gui.Text("", key = const.Layout.CONTACTS_COMPLETED_TEXT),
                            gui.Button(const.Layout.NEXT_BUTTON, key = const.Layout.NEXT_BUTTON)])
        self.layout.append([gui.Button(const.Layout.SAVE_BUTTON, key = const.Layout.SAVE_BUTTON)])

        self.window = gui.Window('VCF duplicate find and merge', self.layout, grab_anywhere = False, element_justification = const.Layout.RIGHT_JUSTIFY)                 
        #self.window.read() #need to finalize the window like this before being able to update any element        

    def runEventLoop(self):#this function should get called repeatedly from an external while loop
        self.event, self.values = self.window.read(timeout = const.Layout.WINDOW_WAIT_TIMEOUT_MILLISECOND) 
        if self.event == gui.WIN_CLOSED or self.event == gui.Exit:#somehow, this line works only if placed above the check for event and values being None
            self.closeWindow()  
        else:
            if self.event == const.Layout.EXPLANATION_BUTTON:
                explainUI = Explanation()        
                explainUI.display()
            if self.event == const.Layout.PREV_BUTTON or self.event == const.Layout.NEXT_BUTTON:
                if self.firstTimeClickingNextPrev:
                    self.__clearBothColumns()
                    duplicateContacts, self.duplicateIndexAtGUI = self.backend.getInfoOfCurrentDuplicate()
                    self.__showContactstoUserOnGUI(duplicateContacts)                    
                    self.firstTimeClickingNextPrev = False
                else:
                    try:
                        self.__saveAnyContactsChangesToMemory()
                    except ValueError:
                        return #avoid advancing forward or backward if the data is corrupted. Allowing the User a chance to fix the data
                    if self.event == const.Layout.NEXT_BUTTON: 
                        self.backend.moveDuplicateIndex(const.GlobalConstants.FORWARD)
                    else: 
                        self.backend.moveDuplicateIndex(const.GlobalConstants.BACKWARD)                 
                    duplicateContacts, self.duplicateIndexAtGUI = self.backend.getInfoOfCurrentDuplicate()
                    self.__showContactstoUserOnGUI(duplicateContacts) 
            if self.event == const.Layout.SAVE_BUTTON:
                errorSaving, numContacts = self.backend.saveContactsToDisk()
                if errorSaving: 
                    if len(errorSaving) > const.GlobalConstants.MAX_LENGTH_OF_ERROR:#truncate a long error message, but make sure it's shown fully in the log
                        log.error(errorSaving)
                        errorSaving = (errorSaving[:const.GlobalConstants.MAX_LENGTH_OF_ERROR] + '...') 
                    SimplePopup(f"Could not save contacts to disk. The error is: {errorSaving}", "Error")
                else: SimplePopup(f"Saved {numContacts} contacts to: {self.backend.getFolderUserChose()}{const.GlobalConstants.DEFAULT_SAVE_FILENAME}{const.GlobalConstants.VCF_EXTENSION}. Any old file with the same name is overwritten.\nContacts won't be in alphabetical order.\nProgram state should have been saved to {const.GlobalConstants.PROGRAM_STATE_SAVE_FILENAME}", "Success")
        return self.event, self.values #for the caller to know when the save button is pressed (to save program state)               
 
    def __saveAnyContactsChangesToMemory(self):
        """ If the user had made any changes to the unique contact or even the duplicate contact, save it to memory """
        uniqueContact = self.values[const.Layout.CONTACTS_DISPLAY_TEXTFIELD]
        duplicateContacts = self.values[const.Layout.DUPLICATES_DISPLAY_TEXTFIELD]
        log.debug(f"Unique Contact {uniqueContact}\n duplicate contact {duplicateContacts}")
        updatedContact = self.__putContactStringsIntoList(uniqueContact, duplicateContacts)
        log.debug(f"updated contact: {updatedContact}")
        self.backend.updateInfoOfCurrentDuplicate(updatedContact)

    def __clearBothColumns(self):
        self.window[const.Layout.CONTACTS_DISPLAY_TEXTFIELD].update("")
        self.window[const.Layout.DUPLICATES_DISPLAY_TEXTFIELD].update("")                

    def __showContactstoUserOnGUI(self, contacts):
        """ Show the contacts in the left and right multiline text boxes """
        log.debug(f"Contacts to display: {contacts}")
        if contacts:
            uniqueContacts = self.__getContactsAsStringsForDisplay(contacts[const.GlobalConstants.FIRST_POSITION_IN_LIST])
            duplicateContacts = self.__getContactsAsStringsForDisplay(contacts[const.GlobalConstants.SECOND_POSITION_IN_LIST])
            self.window[const.Layout.CONTACTS_DISPLAY_TEXTFIELD].update(uniqueContacts)
            self.window[const.Layout.DUPLICATES_DISPLAY_TEXTFIELD].update(duplicateContacts)                            
        else:
            log.error(f"Duplicate contact at index {self.duplicateIndexAtGUI} does not have any data")
        self.window[const.Layout.CONTACTS_COMPLETED_TEXT].update(f"{self.duplicateIndexAtGUI + 1} of {self.numDuplicates}")

    def __getContactsAsStringsForDisplay(self, contacts):
        s = ""
        for contact in contacts:
            s += self.__getContactAsString(contact)
        return s
    
    def __putContactStringsIntoList(self, uniqueContact, duplicateContacts):
        """ each contact needs to be put into a list and all contact lists will be put into a list. That's how it's stored and recognized by the other functions that extract it """
        uniqueContact = uniqueContact.split(const.GlobalConstants.NEWLINE)
        duplicateContacts = duplicateContacts.split(const.GlobalConstants.NEWLINE)
        return [self.__extractIndividualContacts(uniqueContact), self.__extractIndividualContacts(duplicateContacts)] #joining both lists

    def __extractIndividualContacts(self, contacts):
        extractedContacts = []
        contact = None
        numBegins = 0; numEnds = 0
        for line in contacts:
            log.debug(f"The line is: {line}")
            if line:#if the string is not empty
                if line.startswith(const.Properties.BEGIN):
                    contact = [] #create a new contact
                    numBegins += 1
                contact.append(line)
                if line.startswith(const.Properties.END):
                    extractedContacts.append(contact)
                    numEnds += 1
        if numEnds != numBegins:#TODO: more robust data checking could be done based on the VCard version number and required properties
            errorMessage = f"One of the contacts is not in the right format. Please make sure that every contact starts with {const.Properties.BEGIN} and ends with {const.Properties.END}.\n\n Staying at the current contact to allow you a chance to fix it. \n\nThe problematic data is {contacts}"
            log.error(errorMessage)
            SimplePopup(errorMessage, "Data corruption")  
            raise ValueError(errorMessage)          
        return extractedContacts
    
    def __getContactAsString(self, contact):
        s = ""
        for line in contact:
            s += line + const.GlobalConstants.NEWLINE
        s += const.GlobalConstants.NEWLINE #add an extra newline to separate contacts from each other
        return s

    def closeWindow(self):
        self.window.close()
        self.programRunning = False
        
    def checkIfNotClosedGUI(self):
        return self.programRunning


#TODO: Could simplify using gui.popup_get_file (https://www.tutorialspoint.com/pysimplegui/pysimplegui_popup_windows.htm)
class FolderChoiceMenu:
    def __init__(self, fileOps):
        self.event = None
        self.values = None
        self.wrapLength = 70
        self.horizontalSepLen = 35    
        self.fileOps = fileOps  
        self.folderNameStorageFile = const.GlobalConstants.previouslySelectedFolderForDuplicatesCheck
        self.previouslySelectedFolder = None
    
    def showUserTheMenu(self, title, topText, bottomText):
        #---choose mode of running
        layout = []
        layout.append([gui.Text(self.wrap(topText), justification = const.Layout.LEFT_JUSTIFY)])
        self.checkForPreviouslySelectedFolder()
        layout.append([gui.Input(), gui.FolderBrowse(initial_folder = self.previouslySelectedFolder)])
        layout.append([gui.Text(self.wrap(bottomText), text_color = const.Layout.COLOR_GREY, justification = const.Layout.RIGHT_JUSTIFY)])        
        layout.append([gui.Text('_' * self.horizontalSepLen, justification = const.Layout.RIGHT_JUSTIFY, text_color = const.Layout.COLOR_BLACK)])
        layout.append([gui.Button(const.Layout.CANCEL_BUTTON), gui.Button(const.Layout.OK_BUTTON)])        
        window = gui.Window(title, layout, grab_anywhere = False, element_justification = const.Layout.RIGHT_JUSTIFY)    
        self.event, self.values = window.read()        
        window.close()
    
    def getUserChoice(self):
        retVal = None
        if self.event == gui.WIN_CLOSED or self.event == const.Layout.EVENT_EXIT \
                                        or self.event == const.Layout.EVENT_CANCEL \
                                        or self.values[const.GlobalConstants.FIRST_POSITION_IN_LIST] == '':
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

    def wrap(self, text):
        return textwrap.fill(text, self.wrapLength)

class Explanation:
    def __init__(self) -> None:    
        self.wrapLength = 100
        self.boldFont = ('Arial Bold', 14)   
        Explain = namedtuple("Explain", "heading elaboration")
        howItWorks = self.wrap("When you select a folder, this program automatically scans the folder and all subfolders, for VCF files. "
                               "When it loads contacts from each file, it automatically ignores contacts that are exact duplicates of contacts "
                               f"which are already loaded. Then it creates groups of contacts that are similar, based on the last {const.GlobalConstants.NUMBER_OF_TEL_END_DIGITS} characters in the rows of the phone number. "
                               "So now there are unique contacts and groups of duplicate contacts. The GUI then shows you each group of contacts, and "
                               f"you can iterate each group using the '{const.Layout.NEXT_BUTTON}' and '{const.Layout.PREV_BUTTON}' buttons. "
                               "From each group, the first contact is shown on the right, and the duplicates are shown on the left. At any point of time, "
                               f"if you click the {const.Layout.SAVE_BUTTON} button, all unique contacts (won't be shown on the GUI) will get saved to a file named '{const.GlobalConstants.DEFAULT_SAVE_FILENAME}{const.GlobalConstants.VCF_EXTENSION}' "
                               f"and the first contact in each group of duplicates (shown on the right side), will also be saved to the file. This means that if you don't inspect all duplicates before saving"
                               ", the contacts which are not actually duplicates, and were displayed on the left side, won't be saved. Each time you click "
                               f"'{const.Layout.SAVE_BUTTON}', the program will also save progress into a temporary binary file named '{const.GlobalConstants.PROGRAM_STATE_SAVE_FILENAME}', "
                               "so you can close the program and re-open it later, and continue from where you left off. "
                               "\nThe program remembers the path you last specified for searching for VCF files, to avoid having to re-browse for it."                               
                            )
        howToUse = self.wrap(f"Use the '{const.Layout.NEXT_BUTTON}' and '{const.Layout.PREV_BUTTON}' buttons to verify if the duplicates the program detected "
                             "are indeed duplicates. You can copy and paste data between the left and right textboxes. Just make sure you don't mess up the "
                             f"standard VCF format when modifying the data. Click the '{const.Layout.SAVE_BUTTON}' button when done, and you'll find the merged "
                             f"contacts in the '{const.GlobalConstants.DEFAULT_SAVE_FILENAME}{const.GlobalConstants.VCF_EXTENSION}' file which will be in the same "
                             "folder that contains the VCF files."                             
                            )
        textToDisplay = [ Explain("How it works", howItWorks), #the creation of named tuples with the first tuple being the heading and the second being the explanation
                          Explain("How to use", howToUse)
                        ]

        self.layout = []
        for text in textToDisplay:
            self.layout.append([gui.Text(text.heading, font = self.boldFont, justification = const.Layout.LEFT_JUSTIFY)])
            self.layout.append([gui.Text(text.elaboration, expand_y = True, justification = const.Layout.LEFT_JUSTIFY)])
        #self.layout.append([gui.Button(const.Layout.OK_BUTTON)])
                        
    def display(self):
        window = gui.Window(f'Help Information', self.layout, finalize=True, modal=True, element_justification = const.Layout.LEFT_JUSTIFY)
        event, values = window.read()
        window.close()

    def wrap(self, text):
        return textwrap.fill(text, self.wrapLength)
