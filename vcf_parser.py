import os
from loguru import logger as log
from programConstants import constants as const

class OneContact:#stores a single contact
    def __init__(self) -> None:
        self.contact = [] #['BEGIN:VCARD', 'FN:Dr. John Doe', ...]
    
    def addToContact(self, line):
        self.contact.append(line)

    def checkForSimilarity(self, anotherContact):
        pass

class VCF:
    def __init__(self, fileOps) -> None:
        self.fileOps = fileOps
        self.allContacts = []

    def loadVCF(self, folderName):
        filesWithFullPath = self.__getAllFilesToProcess(folderName)
        for aFile in filesWithFullPath:
            loadedContacts = self.__loadData(aFile)

    def __loadData(self, filenameWithPath):
        lines = self.fileOps.readFromFile(filenameWithPath)
        numLines = len(lines)
        i = const.GlobalConstants.FIRST_POSITION_IN_LIST
        allContacts = []
        recording = False
        while i < numLines:
            currentline = lines[i]
            if currentline.startswith(const.Properties.BEGIN):
                contact = OneContact() #create new contact
                recording = True                          
            if recording:
                contact.addToContact(lines[i])
            if currentline.startswith(const.Properties.END):
                recording = False                  
                allContacts.append(contact)
            i = i + 1
        if len(allContacts) == 0: log.warning(f"No contacts were detected in {filenameWithPath}")
        else: log.info(f"{len(allContacts)} contacts loaded from {filenameWithPath}")
        return allContacts

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
