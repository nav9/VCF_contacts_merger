import os
from loguru import logger as log
from collections import deque
from programConstants import constants as const

# class OneContact:#stores a single contact
#     def __init__(self) -> None:
#         self.contact = [] #['BEGIN:VCARD', 'FN:Dr. John Doe', ...]
#         self.possibleDuplicate = False #When the searching function goes through all contacts to find similar contacts, if it finds this contact similar to another, it'll mark this True, so that in future iterations, time is not wasted in comparing this contact with other contacts
    
#     def addToContact(self, line):
#         self.contact.append(line)
#         #TODO: extract name and phone

#     def checkForSimilarity(self, anotherContact):
#         similar = False
#         if self.possibleDuplicate:
#             pass
#         else:
#             #TODO: check for similarity
#             if similar:
#                 self.possibleDuplicate = True
#         return similar

class VCF:
    def __init__(self, fileOps) -> None:
        self.fileOps = fileOps
        self.allContacts = deque()
        self.totalContactsProcessed = 0
        self.contactsDiscarded = 0
        self.duplicates = [] #[[1,7,9], [2,90,340], ...] #each internal list is a bunch of indices of contacts of self.allContacts, where the phone numbers are similar. Later, we present these contacts to the User and ask them to sort it out

    def loadVCF(self, folderName):
        """ Load each contact in each VCF file, and ignore exact matches to already loaded contacts """        
        filesWithFullPath = self.__getAllFilesToProcess(folderName)
        for aFile in filesWithFullPath:
            self.__readData(aFile) #loads each contact as a list of all components of the contact, and stores them in self.allContacts
        log.info(f"{self.totalContactsProcessed} contacts were loaded from {len(filesWithFullPath)} files.")
        log.info(f"{self.contactsDiscarded} contacts were exact duplicates of previously loaded contacts.")
        log.info(f"So now there are {len(self.allContacts)} contacts.")
        assert(len(self.allContacts) == (self.totalContactsProcessed - self.contactsDiscarded)) #ensure that there are no contacts missed
        return len(self.allContacts)

    def searchForDuplicateContactsBasedOnPhoneNumber(self):
        indexOfDuplicates = set() #indices of contacts with similar phone numbers that were already found
        for i in range(len(self.allContacts)-1):
            duplicate = []
            iPhoneNumbers = self.__getLast8digitsOfPhoneNumber(i)
            for j in range(i+1, len(self.allContacts)):
                if j in indexOfDuplicates: continue #skip any duplicate index that was already found                    
                else:
                    if iPhoneNumbers.intersection(self.__getLast8digitsOfPhoneNumber(j)):#common partial match of phone numbers were found
                        indexOfDuplicates.add(j)
                        duplicate.append(j)
            if duplicate:#at least one duplicate found
                duplicate.insert(const.GlobalConstants.FIRST_POSITION_IN_LIST, i)#add i to the beginning of the list
                self.duplicates.append(duplicate)  
        
    def showDuplicateContactsFound(self):
        for duplicate in self.duplicates:
            for contact in duplicate:
                print(self.allContacts[contact])
            print('-------------------------')

    def __getLast8digitsOfPhoneNumber(self, index):
        """ returns a set of the last 8 digits of all phone numbers found in this contact """
        phoneNumbers = set()
        contact = self.allContacts[index]
        delimiters = [const.GlobalConstants.COLON_DELIMITER, const.GlobalConstants.SEMICOLON_DELIMITER]
        for entry in contact:
            if entry.startswith(const.Properties.TEL):
                #---create a list of the entries without : or ;. Eg: 'TEL;CELL;PREF:*121#' becomes ['TEL', 'CELL', 'PREF', '*121#']
                for delimiter in delimiters:
                    entry = " ".join(entry.split(delimiter))
                entry = entry.split()
                #---search backward for any part that contains at least one number
                phoneNumber = None
                for val in reversed(entry):#search the entry backward
                    if any(char.isdigit() for char in val):#a number is present in this string, so it might be a phone number
                        phoneNumber = val
                        break
                if phoneNumber:
                    if len(phoneNumber) >= const.GlobalConstants.NUMBER_OF_TEL_END_DIGITS:
                        phoneNumber = phoneNumber[-const.GlobalConstants.NUMBER_OF_TEL_END_DIGITS:]#get the last 8 digits
                    phoneNumbers.add(phoneNumber)
        return phoneNumbers

    def __readData(self, filenameWithPath):
        lines = self.fileOps.readFromFile(filenameWithPath)
        numLines = len(lines)
        i = const.GlobalConstants.FIRST_POSITION_IN_LIST
        #allContacts = [] #stores a list of OneContact object references
        contact = list()
        recording = False
        contactsProcessed = 0
        duplicatesFound = 0
        numberOfBeginsDetected = 0
        numberOfEndsDetected = 0        
        while i < numLines:#iterate the entire file
            currentline = lines[i]
            if currentline.startswith(const.Properties.BEGIN):
                numberOfBeginsDetected += 1
                contact = [] #create new contact
                recording = True                          
            if recording:
                contact.append(currentline)
            if currentline.startswith(const.Properties.END):
                contactsProcessed += 1; numberOfEndsDetected += 1
                recording = False                  
                if self.__isExactContactAlreadyPresent(contact): duplicatesFound += 1
                else: self.allContacts.append(contact)
            i += 1
        if contactsProcessed == 0: log.warning(f"No contacts were detected in {filenameWithPath}")
        else: log.info(f"{contactsProcessed} contacts loaded ({duplicatesFound} were exact duplicates of previously loaded contacts) from {filenameWithPath}")
        self.contactsDiscarded += duplicatesFound
        self.totalContactsProcessed += contactsProcessed
        if numberOfBeginsDetected != numberOfEndsDetected:
            raise ValueError(f"File {filenameWithPath} appears to be corrupted. Number of {const.Properties.BEGIN} tags = {numberOfBeginsDetected}, but number of {const.Properties.END} = {numberOfEndsDetected}. Please examine the file or remove it from the folder.")        

    def __isExactContactAlreadyPresent(self, contact):
        """ Checks if the contact is an exact duplicate of any existing contact """
        present = False
        for oneContact in self.allContacts:
            if oneContact == contact:
                present = True
                break #breaks out of for loop
        return present

    def __getAllFilesToProcess(self, folderName):
        filesToProcess = []
        folderPaths, filesInFolder, fileSizes = self.fileOps.getFileNamesOfFilesInAllFoldersAndSubfolders(folderName) #returns as [fullFolderPath1, fullFolderPath2, ...], [[filename1, filename2, filename3, ...], [], []], [[filesize1, filesize2, filesize3, ...], [], []]
        i = const.GlobalConstants.FIRST_POSITION_IN_LIST
        for folder in folderPaths:
            for filename in filesInFolder[i]:#iterate files in folder
                file_name, fileExtension = self.fileOps.getFilenameAndExtension(filename)
                if fileExtension.lower() == const.GlobalConstants.VCF_EXTENSION:
                    filesToProcess.append(os.path.join(folder, filename))
        return filesToProcess
