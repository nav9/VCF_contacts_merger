import textwrap
import PySimpleGUI as gui
from programConstants import constants as const
from loguru import logger as log
             
#-----------------------------------------------
#-------------------- MENUS --------------------
#-----------------------------------------------

class SimplePopup:
    def __init__(self, message, popupTitle) -> None:
        gui.Popup(message, title=popupTitle)

class ContactsChoiceGUI:
    def __init__(self):
        self.event = None
        self.values = None
        self.horizontalSepLen = 90    
        self.multilineTextboxWidth = 40
        self.multilineTextboxHeight = 20
        self.layout = []
        self.backend = None
        self.window = None
        self.programRunning = True
        self.duplicateIndexAtGUI = None
        self.numDuplicates = None
    
    def addBackendOfVCF(self, backendRef):
        self.backend = backendRef

    def createGUI(self):
        totalContacts = self.backend.getNumberOfContacts()
        self.numDuplicates = self.backend.getNumberOfDuplicates()
        duplicateContacts, self.duplicateIndexAtGUI = self.backend.getInfoOfCurrentDuplicate()
        self.layout.append([gui.Button(const.Layout.HOW_TO_USE_BUTTON, key = const.Layout.HOW_TO_USE_BUTTON)])
        topText = [f"The program has {totalContacts} contacts in memory, of which {self.numDuplicates} appear to have duplicates."]        
        for s in topText:
            self.layout.append([gui.Text(s, text_color = const.Layout.COLOR_GREY, justification = const.Layout.LEFT_JUSTIFY)])    
        self.layout.append([gui.Text('_' * self.horizontalSepLen, justification = const.Layout.RIGHT_JUSTIFY, text_color = const.Layout.COLOR_GREY)])
        contactColumnTitle = gui.Text("Contact(s) that will be saved")
        contactsDisplay = gui.Multiline(f"Start by clicking\n the {const.Layout.NEXT_BUTTON} button below", size = (self.multilineTextboxWidth, self.multilineTextboxHeight), key = const.Layout.CONTACTS_DISPLAY_TEXTFIELD, horizontal_scroll = True, do_not_clear = True)
        duplicatesColumnTitle = gui.Text("Assumed duplicates of the contact on the right")
        duplicatesDisplay = gui.Multiline(size = (self.multilineTextboxWidth, self.multilineTextboxHeight), key = const.Layout.DUPLICATES_DISPLAY_TEXTFIELD, horizontal_scroll = True, do_not_clear = True)
        leftColumn = [[duplicatesColumnTitle], [duplicatesDisplay]]
        rightColumn = [[contactColumnTitle], [contactsDisplay]]
        self.layout.append([gui.Column(leftColumn), gui.Column(rightColumn)])
        self.layout.append([gui.Button(const.Layout.PREV_BUTTON, key = const.Layout.PREV_BUTTON), 
                            gui.Text("", key = const.Layout.CONTACTS_COMPLETED_TEXT),
                            gui.Button(const.Layout.NEXT_BUTTON, key = const.Layout.NEXT_BUTTON)])
        self.layout.append([gui.Button(const.Layout.SAVE_BUTTON, button_color = 'black on yellow', key = const.Layout.SAVE_BUTTON)])

        self.window = gui.Window('VCF duplicate find and merge', self.layout, grab_anywhere = False, element_justification = const.Layout.RIGHT_JUSTIFY)                 
        self.window.read() #need to finalize the window like this before being able to update any element
        self.__showContactstoUserOnGUI(duplicateContacts)

    def runEventLoop(self):#this function should get called repeatedly from an external while loop
        self.event, self.values = self.window.read(timeout = const.Layout.WINDOW_WAIT_TIMEOUT_MILLISECOND) 
        if self.event == gui.WIN_CLOSED or self.event == gui.Exit:#somehow, this line works only if placed above the check for event and values being None
            self.closeWindow()  
        else:
            if self.event == const.Layout.HOW_TO_USE_BUTTON:
                SimplePopup(self.__getHelpInformation(), "How to use the GUI")               
            if self.event == const.Layout.PREV_BUTTON or self.event == const.Layout.NEXT_BUTTON:
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
 
    def __saveAnyContactsChangesToMemory(self):
        """ If the user had made any changes to the unique contact or even the duplicate contact, save it to memory """
        uniqueContact = self.values[const.Layout.CONTACTS_DISPLAY_TEXTFIELD]
        duplicateContacts = self.values[const.Layout.DUPLICATES_DISPLAY_TEXTFIELD]
        log.debug(f"Unique Contact {uniqueContact}\n duplicate contact {duplicateContacts}")
        updatedContact = self.__putContactStringsIntoList(uniqueContact, duplicateContacts)
        log.debug(f"updated contact: {updatedContact}")
        self.backend.updateInfoOfCurrentDuplicate(updatedContact)

    def __showContactstoUserOnGUI(self, contacts):
        """ Show the contacts in the left and right multiline text boxes """
        log.debug(f"Contacts to display: {contacts}")
        #firstContact = True
        if contacts:
            uniqueContacts = self.__getContactsAsStringsForDisplay(contacts[const.GlobalConstants.FIRST_POSITION_IN_LIST])
            duplicateContacts = self.__getContactsAsStringsForDisplay(contacts[const.GlobalConstants.SECOND_POSITION_IN_LIST])
            self.window[const.Layout.CONTACTS_DISPLAY_TEXTFIELD].update(uniqueContacts)
            self.window[const.Layout.DUPLICATES_DISPLAY_TEXTFIELD].update(duplicateContacts)                
            # for contact in contacts:
            #     if firstContact:#show the unique contact on the right textfield
            #         self.window[const.Layout.CONTACTS_DISPLAY_TEXTFIELD].update(self.__getContactAsString(contact))
            #         firstContact = False
            #     else:#show the duplicate contacts on the left textfield
            #         self.window[const.Layout.DUPLICATES_DISPLAY_TEXTFIELD].update(self.__getContactAsString(contact))                
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
            if line:#if the string is not empty
                if line.startswith(const.Properties.BEGIN):
                    contact = [] #create a new contact
                    numBegins += 1
                contact.append(line)
                if line.startswith(const.Properties.END):
                    extractedContacts.append(contact)
                    numEnds += 1
        if numEnds != numBegins:
            errorMessage = f"One of the contacts is not in the right format. Please make sure that every contact starts with {const.Properties.BEGIN} and {const.Properties.END}. \n\nThe problematic data is {contacts}"
            log.error(errorMessage)
            SimplePopup(errorMessage, "Error in contact")  
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

    def __getHelpInformation(self):
        wrapLength = 150
        info = (f"How it works:{const.GlobalConstants.NEWLINE}"
                "When you select a folder, this program automatically scans the folder and all subfolders, for VCF files."
                "When it loads contacts from each file, it automatically ignores contacts that are exact duplicates of contacts"
                f"which are already loaded. Then it creates groups of contacts that are similar, based on the last {const.GlobalConstants.NUMBER_OF_TEL_END_DIGITS} digits of the phone number."
                "So now there are unique contacts and groups of duplicate contacts. The GUI then shows you each group of contacts, and"
                f"you can iterate each group using the {const.Layout.NEXT_BUTTON} and {const.Layout.PREV_BUTTON} buttons."
                "From each group, the first contact is shown on the right, and the duplicates are shown on the left. At any point of time,"
                f"if you click the {const.Layout.SAVE_BUTTON} button, all individual contacts will get saved to a file named {const.GlobalConstants.DEFAULT_SAVE_FILENAME}{const.GlobalConstants.VCF_EXTENSION}"
                f"and the first contact in each group of duplicates (shown on the right side), will also be saved to the file. This means that if you don't inspect all duplicates before saving"
                ", the contacts which are not actually duplicates, and were displayed on the left side, won't be saved. Each time you click"
                f"{const.Layout.SAVE_BUTTON}, the program will also save progress into a temporary binary file named {const.GlobalConstants.TEMP_FILENAME},"
                "so you can close the program and re-open it later, and continue from where you left off."
                f"The program remembers the path you last specified for searching for VCF files, to avoid having to re-browse for it.{const.GlobalConstants.NEWLINE}"
                f"How to use:{const.GlobalConstants.NEWLINE}"
                f"Use the {const.Layout.NEXT_BUTTON} and {const.Layout.PREV_BUTTON} buttons to verify if the duplicates the program detected"
                "are indeed duplicates. You can copy and paste data between the left and right textboxes. Just make sure you don't mess up the"
                f"standard VCF format when modifying the data. Click the {const.Layout.SAVE_BUTTON} button when done, and you'll find the merged"
                f"contacts in the {const.GlobalConstants.DEFAULT_SAVE_FILENAME}{const.GlobalConstants.VCF_EXTENSION} file which will be in the same."
                "folder that contains the VCF files."
                )
        info = textwrap.fill(info, wrapLength)
        return info

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

