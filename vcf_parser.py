import os
import datetime
from loguru import logger as log
from collections import deque
from programConstants import constants as const

class VCF:
    def __init__(self, fileOps, folderChosen) -> None:
        self.fileOps = fileOps
        self.folderChosen = folderChosen
        self.allContacts = deque() #each contact is a list like ['BEGIN:VCARD', 'VERSION:2.1', 'N:;John;;;', 'FN:John Doe', 'TEL;CELL;PREF:000000000', 'END:VCARD']
        self.totalContactsProcessed = 0
        self.contactsDiscarded = 0
        self.duplicates = [] #[[1,7,9], [2,90,340], ...] or [[[values of unique contacts from self.allContacts], [values of duplicate contacts from self.allContacts]], ...] #each internal list is a bunch of indices of contacts of self.allContacts, where the phone numbers are similar. Later, we present these contacts to the User and ask them to sort it out. After determining duplicates, the indices are replaced with actual contact's values
        self.duplicateIndexAtGUI = 0
        self.indicesOfAllDuplicates = set() #indices of contacts with similar phone numbers that were already found
        self.indicesOfUniqueContacts = set() #indices of contacts which have no duplicates
        self.filesWithFullPath = None
        self.phoneNumberComparison = dict() #{index of contact: set of last 8 digits of phone numbers of the contact}

    def whichFilesWereConsideredVCF(self):#this will be called from the GUI too
        return self.filesWithFullPath
    
    def getNumberOfContacts(self):#this will be called from the GUI too
        return len(self.allContacts)
    
    def getNumberOfDuplicates(self):#this will be called from the GUI too
        return len(self.duplicates)
    
    def getInfoOfCurrentDuplicate(self):#this will be called from the GUI
        return self.duplicates[self.duplicateIndexAtGUI], self.duplicateIndexAtGUI #returns a contact like ['BEGIN:VCARD', 'VERSION:2.1', 'N:;John;;;', 'FN:John Doe', 'TEL;CELL;PREF:000000000', 'END:VCARD']
    
    def updateInfoOfCurrentDuplicate(self, updatedContact):#this will be called from the GUI
        self.duplicates[self.duplicateIndexAtGUI] = updatedContact #will have to be a list like ['BEGIN:VCARD', 'VERSION:2.1', 'N:;John;;;', 'FN:John Doe', 'TEL;CELL;PREF:000000000', 'END:VCARD']
    
    def saveContactsToDisk(self):#this will be called from the GUI
        """ Saves the unique contacts into a VCF file """  
        numContacts = 0    
        contactsToSave = []
        #---collect unique contacts
        numContacts += len(self.indicesOfUniqueContacts)
        for uniqueContactIndex in self.indicesOfUniqueContacts:
            contactsToSave = contactsToSave + self.allContacts[uniqueContactIndex] #merging each line of the contact into the contactsToSave list so that it gets written line by line
        #---collect the unique contact in all duplicates
        for duplicate in self.duplicates:
            for contact in duplicate[const.GlobalConstants.FIRST_POSITION_IN_LIST]:
                numContacts += 1
                contactsToSave = contactsToSave + contact #merging each line of the contact into the contactsToSave list so that it gets written line by line
        #---write
        saveFileName = os.path.join(self.folderChosen, const.GlobalConstants.DEFAULT_SAVE_FILENAME + datetime.date.today().strftime("%d%B%Y") + const.GlobalConstants.VCF_EXTENSION)
        errorSaving = self.fileOps.writeLinesToFile(saveFileName, contactsToSave)
        return errorSaving, numContacts, saveFileName #value will be None if successful save. Else, it'll contain the error message
    
    def moveDuplicateIndex(self, direction):#this will be called from the GUI
        if direction == const.GlobalConstants.FORWARD:
            if self.duplicateIndexAtGUI < self.getNumberOfDuplicates() - 1:
                self.duplicateIndexAtGUI += const.GlobalConstants.FORWARD
        if direction == const.GlobalConstants.BACKWARD:
            if self.duplicateIndexAtGUI > const.GlobalConstants.FIRST_POSITION_IN_LIST:
                self.duplicateIndexAtGUI += const.GlobalConstants.BACKWARD #the value of BACKWARD is -1        

    def loadVCF(self, folderName):
        """ Load each contact in each VCF file, and ignore exact matches to already loaded contacts """        
        self.filesWithFullPath = self.__getAllFilesToProcess(folderName)
        for aFile in self.filesWithFullPath:
            self.__readData(aFile) #loads each contact as a list of all components of the contact, and stores them in self.allContacts
        log.info(f"{self.totalContactsProcessed} contacts were loaded from {len(self.filesWithFullPath)} files.")
        log.info(f"{self.contactsDiscarded} contacts were exact duplicates of previously loaded contacts.")
        log.info(f"So now there are {self.getNumberOfContacts()} contacts.")
        assert(self.getNumberOfContacts() == (self.totalContactsProcessed - self.contactsDiscarded)) #ensure that there are no contacts missed        
        return self.getNumberOfContacts(), self.getNumberOfDuplicates()

    def searchForDuplicateContactsBasedOnPhoneNumber(self): 
        self.duplicates.clear()
        duplicateBuckets = deque() #[  [set(phone numbers), set(duplicate indices of the phone numbers)],  [set(), set()],  ...  ] #each [set(), set()] is a bucket
        log.info(f"Searching {self.getNumberOfContacts()} for duplicates")
        self.__addPhoneNumberDuplicatesToBucket(duplicateBuckets)
        print(f"BEFORE MERGING {len(duplicateBuckets)}")
        duplicateBuckets = self.__mergeBucketsHavingCommonIndices(duplicateBuckets) #the deque returned will be a new deque which has the duplicates removed and the buckets with common values merged
        print(f"AFTER MERGING {len(duplicateBuckets)}")
        #---now the buckets will have duplicate indices and non duplicate ones. Search
        #TODO: if a contact does not have a phone number, consider checking such contacts for duplicates based on name or email id
        for bucket in duplicateBuckets:
            #phoneNumbers = bucket[const.GlobalConstants.FIRST_POSITION_IN_LIST] #there's a chance that a phone number may not be present, and that's normal
            indices = bucket[const.GlobalConstants.SECOND_POSITION_IN_LIST] #there has to be at least one index. Because a bucket is created for any valid index or indices
            if len(indices) == 1:#index of a unique contact
                self.indicesOfUniqueContacts = self.indicesOfUniqueContacts.union(indices)
            if len(indices) > 1:#indices of contacts with duplicates
                self.indicesOfAllDuplicates = self.indicesOfAllDuplicates.union(indices)
                self.duplicates.append(list(indices))
            if len(indices) == 0: raise ValueError("A bucket does not have any indices. This should never happen. Buckets should be created only if there are some indices related to it.")
        #---check for errors
        displayMessage = f"Number of duplicates: {len(self.indicesOfAllDuplicates)}. Number of unique contacts: {len(self.indicesOfUniqueContacts)}. Total contacts: {len(self.allContacts)}. "
        if len(self.indicesOfAllDuplicates) + len(self.indicesOfUniqueContacts) != len(self.allContacts): raise ValueError(displayMessage + "The sum of duplicates and unique contacts should be equal to total contacts. If not, there's some bug in the code.")
        else: log.info(displayMessage)   
        log.info(f"Number of groups of duplicates = {len(self.duplicates)}")
        #---prepare the duplicates for displaying in the GUI     
        self.__replaceDuplicateIndicesWithActualValues()
        return self.getNumberOfDuplicates() 

    def __addPhoneNumberDuplicatesToBucket(self, duplicateBuckets):#passing duplicateBuckets by reference
        #duplicateBuckets is a list() like this: [  [set(phone numbers), set(duplicate indices of the phone numbers)],  [set(), set()],  ...  ]. Each [set(), set()] is a bucket.
        for i in range(self.getNumberOfContacts()):
            phoneNumbersAt_i = self.__getLast8digitsOfPhoneNumber(i) #returns a set of numbers
            noPhoneNumberMatched = True
            for bucket in duplicateBuckets:#go through all existing buckets created
                phoneNumbers = bucket[const.GlobalConstants.FIRST_POSITION_IN_LIST]
                if phoneNumbers.intersection(phoneNumbersAt_i):#are any of the phone numbers present in the bucket's phone numbers?
                    noPhoneNumberMatched = False
                    bucket[const.GlobalConstants.FIRST_POSITION_IN_LIST] = phoneNumbers.union(phoneNumbersAt_i) #add these phone numbers as they are part of the duplicate
                    bucket[const.GlobalConstants.SECOND_POSITION_IN_LIST].add(i) #add this index to the bucket's list of indices
            if noPhoneNumberMatched:#create a new entry
                duplicateBuckets.append([phoneNumbersAt_i, set({i})])

    def __mergeBucketsHavingCommonIndices(self, duplicateBuckets):
        for bucket in duplicateBuckets:
            if bucket == None: continue
            indices = bucket[const.GlobalConstants.SECOND_POSITION_IN_LIST]
            for bucketSearch in duplicateBuckets:
                if bucketSearch == None or bucket == bucketSearch: continue                
                indicesSearched = bucketSearch[const.GlobalConstants.SECOND_POSITION_IN_LIST]
                if indices.intersection(indicesSearched):#if any of the indices match, merge into the bucket
                    phoneNumbersSearched = bucketSearch[const.GlobalConstants.FIRST_POSITION_IN_LIST]
                    bucket[const.GlobalConstants.FIRST_POSITION_IN_LIST] = bucket[const.GlobalConstants.FIRST_POSITION_IN_LIST].union(phoneNumbersSearched)
                    bucket[const.GlobalConstants.SECOND_POSITION_IN_LIST] = bucket[const.GlobalConstants.SECOND_POSITION_IN_LIST].union(indicesSearched)
                    bucketSearch = None #mark it as empty, since the values are already merged into the other bucket
        #---remove any buckets that are None
        mergedBuckets = deque()
        for bucket in duplicateBuckets:
            if bucket != None: mergedBuckets.append(bucket) #copy all buckets that are not None
        return mergedBuckets
                    
    def __replaceDuplicateIndicesWithActualValues(self):   
        """ Replacing indices with values because the actual values are what will be shown and edited in the GUI """   
        #The values will originally be like this: [[1,7,9,10],   [2,90,340], ...] 
        #They need to be changed to be like this: [ [[['BEGIN:VCARD', 'FN:UniqueContact1', ...]], [[['BEGIN:VCARD', 'FN:DuplicateContact1', ...], ['BEGIN:VCARD', 'FN:DuplicateContact2', ...]]], ... ]
        #So essentially, they become like: [[ [[1]], [[7], [9], [10]] ],    [ [[2]], [[90], [340]] ],    ... , ], but the numbers in this line are only meant to show how the original index values are represented here. In this line, in place of the numbers, the actual strings from the contacts will be present
        intervalToOutputLog = 100        
        for i in range(len(self.duplicates)):#duplicate will be a list of indices of self.allContacts. Eg: [2,6,34]            
            if i % intervalToOutputLog == 0: log.info(f"Contact {i} of {len(self.duplicates)} being readied for GUI")
            #---take the first element from the group of duplicates
            uniqueContact = self.duplicates[i][const.GlobalConstants.FIRST_POSITION_IN_LIST] #get the index value
            uniqueContact = self.allContacts[uniqueContact] #get the contact from the index value. This will be a list like ['BEGIN:VCARD', 'FN:UniqueContact1', ...] 
            #---take the remaining elements from the group of duplicates
            duplicateContacts = []
            for j in range(const.GlobalConstants.SECOND_POSITION_IN_LIST, len(self.duplicates[i])):
                oneContact = self.duplicates[i][j] #get the index value
                oneContact = self.allContacts[oneContact] #get the contact from the index value. This will be a list like ['BEGIN:VCARD', 'FN:UniqueContact1', ...] 
                duplicateContacts.append(oneContact)
            #---put the unique contact and the duplicate contact values into the duplicates list
            self.duplicates[i] = [[uniqueContact], duplicateContacts]
            
    def showDuplicateContactsFound(self):
        for duplicate in self.duplicates:
            for contact in duplicate:
                print(self.allContacts[contact])
            print('-------------------------')

    def __getLast8digitsOfPhoneNumber(self, index):
        """ returns a set of the last 8 digits (or lesser digits if shorter than 8) of all phone numbers found in this contact """
        if index in self.phoneNumberComparison:
            if self.phoneNumberComparison[index]:#it had already been computed and stored, so just return the set
                return self.phoneNumberComparison[index]
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
        self.phoneNumberComparison[index] = phoneNumbers                    
        return phoneNumbers

    def __readData(self, filenameWithPath):
        log.info(f"Loading contacts from {filenameWithPath}")
        lines = self.fileOps.readFromFile(filenameWithPath)
        numLines = len(lines)
        i = const.GlobalConstants.FIRST_POSITION_IN_LIST
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
