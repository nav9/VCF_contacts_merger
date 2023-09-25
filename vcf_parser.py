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

    def loadVCF(self, folderName):
        filesWithFullPath = self.__getAllFilesToProcess(folderName)
        for aFile in filesWithFullPath:
            self.__loadData(aFile)

    def __loadData(self, filenameWithPath):
        lines = self.fileOps.readFromFile(filenameWithPath)
        numLines = len(lines)
        i = const.GlobalConstants.FIRST_POSITION_IN_LIST
        #allContacts = [] #stores a list of OneContact object references
        contact = list()
        recording = False
        contactsProcessed = 0
        duplicatesFound = 0
        while i < numLines:#iterate the entire file
            currentline = lines[i]
            if currentline.startswith(const.Properties.BEGIN):
                contact = [] #create new contact
                recording = True                          
            if recording:
                contact.append(currentline)
            if currentline.startswith(const.Properties.END):
                contactsProcessed = contactsProcessed + 1
                recording = False                  
                if self.__isExactContactAlreadyPresent(contact): duplicatesFound = duplicatesFound + 1
                else: self.allContacts.append(contact)
            i = i + 1
        if contactsProcessed == 0: log.warning(f"No contacts were detected in {filenameWithPath}")
        else: log.info(f"{contactsProcessed} contacts loaded ({duplicatesFound} were exact duplicates of previously loaded contacts) from {filenameWithPath}")

    def __isExactContactAlreadyPresent(self, contact):
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
