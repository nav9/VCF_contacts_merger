import os
import shutil #for moving file
import pickle
from loguru import logger as log

#-----------------------------------------------             
#-----------------------------------------------
#------------------ FILE OPS -------------------
#-----------------------------------------------
#-----------------------------------------------

class FileOperations:
    def __init__(self):
        self.FULL_FOLDER_PATH = 0
        self.SUBDIRECTORIES = 1 #Running next() on the generator of os.walk() returns a list of lists. Position 1 of the list is the list of folders
        self.FILES_IN_FOLDER = 2 #Running next() on the generator of os.walk() returns a list of lists. Position 2 of the list is the list of files
        self.LINES_TO_READ_AT_ONCE = 10 * 1024 #can be larger, depending on memory available  
    
    """ Get names of files in each folder and subfolder. Also get sizes of files """
    def getFileNamesOfFilesInAllFoldersAndSubfolders(self, folderToConsider): 
        #TODO: read-only files, files without permission to read, files that can't be moved, corrupted files
        #TODO: What about "file-like objects"
        folderPaths = []; filesInFolder = []; fileSizes = []
        log.info("Obtaining a list of folders and files...")
        result = os.walk(folderToConsider, followlinks=False) #Won't throw an error if folder does not exist. followlinks=False allows skipping symlinks. It's False by default. Just making it obvious here
        log.info("Walking to collect names of files in this folder: " + str(folderToConsider))
        for oneFolder in result:
            folderPath = self.folderSlash(oneFolder[self.FULL_FOLDER_PATH])
            folderPaths.append(folderPath)
            #subdir = oneFolder[self.SUBDIRECTORIES]
            filesInThisFolder = oneFolder[self.FILES_IN_FOLDER]
            filesNotFound = []
            sizeOfFiles = []
            for filename in filesInThisFolder:
                try:
                    fileProperties = os.stat(folderPath + filename)
                    sizeOfFiles.append(fileProperties.st_size)
                except FileNotFoundError:
                    filesNotFound.append(filename)
                    pass #ignore files that are not found. It may be a broken symlink or a file that was deleted in-between or a file on a connected device that got disconnected
            filesInThisFolder = [filename for filename in filesInThisFolder if filename not in filesNotFound] #remove any files not found, from the list
            fileSizes.append(sizeOfFiles)
            filesInFolder.append(filesInThisFolder)            
        return folderPaths, filesInFolder, fileSizes #returns as [fullFolderPath1, fullFolderPath2, ...], [[filename1, filename2, filename3, ...], [], []], [[filesize1, filesize2, filesize3, ...], [], []]
   
    def isValidFile(self, filenameWithPath):
        return os.path.isfile(filenameWithPath)   
    
    def getFilenameAndExtension(self, filenameOrPathWithFilename):
        filename, fileExtension = os.path.splitext(filenameOrPathWithFilename)
        return filename, fileExtension
        
    def writeLinesToFile(self, filenameWithPath, linesToWrite):#linesToWrite can be a list or set
        errorSaving = None
        try:
            fileHandle = open(filenameWithPath, 'w')
            for line in linesToWrite:
                fileHandle.write(line)
                fileHandle.write("\n")
            fileHandle.close()
        except Exception as e:
            errorSaving = f"Error {str(e)} when writing {linesToWrite} to {filenameWithPath}"
            log.error(errorSaving)
        return errorSaving
        
    def writeKeysOfDictToFile(self, filenameWithPath, dictReference):
        fileHandle = open(filenameWithPath, 'w')
        for key in dictReference:
            fileHandle.write(key)
            fileHandle.write("\n")
        fileHandle.close()
        
    def readFromFile(self, filenameWithPath):
        with open(filenameWithPath) as fileHandle:
            lines = fileHandle.read().splitlines()#TODO: try catch
        return lines
    
    #TODO: Consider if it'd be more efficient to load multiple rows as chunks. Or whether yield already does that
    def getGeneratorObjectToFileForReadingLines(self, filenameWithPath):#invoke this function to get the generator object and then just keep calling next(generatorObject) to get each row one by one
        for row in open(filenameWithPath, "r"):
            yield row #returns a generator object
    
    def readBunchOfLinesFromTextFile(self, generatorObject):
        lines = []
        for _ in range(self.LINES_TO_READ_AT_ONCE):
            try:
                line = next(generatorObject)
            except StopIteration:#reached end of file
                break #exit for loop
            lines.append(line)
        return lines #if lines is empty, we've reached the end of the file
    
    def createDirectoryIfNotExisting(self, folder):
        if not os.path.exists(folder): 
            try: os.makedirs(folder)
            except FileExistsError:#in case there's a race condition where some other process creates the directory before makedirs is called
                pass
            
    def getCurrentDirectory(self):
        return os.getcwd()
    
    def isThisValidDirectory(self, folderpath):
        return os.path.exists(folderpath)
    
    def deleteFolderIfItExists(self, folderPath):
        try:
            if os.path.exists(folderPath):
                shutil.rmtree(folderPath, ignore_errors = True) #The ignore_errors is for when the folder has read-only files https://stackoverflow.com/a/303225/453673
        except Exception as e:
            log.error("Error when deleting folder: " + folderPath + ". Exception: " + str(e))

    def deleteFileIfItExists(self, filenameWithPath):
        try:
            if os.path.isfile(filenameWithPath):
                os.remove(filenameWithPath)
        except Exception as e:
            log.error("Error when deleting file: " + filenameWithPath + ". Exception: " + str(e))

    """ Move file to another directory. Renaming while moving is possible """
    def moveFile(self, existingPath, existingFilename, newPath, newFilename):
        pathToMovedFile = None
        try:
            pathToMovedFile = shutil.move(existingPath + existingFilename, newPath + newFilename)    
        except FileNotFoundError:
            log.error("Could not find file: " + existingPath + existingFilename + " when trying to move it to " + newPath + newFilename)
        return pathToMovedFile

    """ Copy file to another directory. Renaming while moving is possible.  If destination specifies a directory, the file will be copied into destination using the base filename from the source. If destination specifies a file that already exists, it will be replaced. """
    def copyFile(self, filenameWithPath, destinationFolderOrFileWithPath):
        pathToCopiedFile = None
        try:
            pathToCopiedFile = shutil.copy2(filenameWithPath, destinationFolderOrFileWithPath)
        except FileNotFoundError:
            log.error("Could not find file: " + filenameWithPath + " or folder " + destinationFolderOrFileWithPath)    
        return pathToCopiedFile
    
    """ Adds a slash at the end of the folder name if it isn't already present """
    def folderSlash(self, folderName):
        return os.path.join(folderName, "") #https://stackoverflow.com/questions/2736144/python-add-trailing-slash-to-directory-string-os-independently

    def saveToPickleFile(self, data, filenameWithPath):
        with open(filenameWithPath, 'wb') as fileHandle:
            pickle.dump(data, fileHandle, pickle.HIGHEST_PROTOCOL)        
    
    def loadFromPickleFile(self, filenameWithPath):
        with open(filenameWithPath, 'rb') as fileHandle:
            data = pickle.load(fileHandle)
        return data
            
    def getListOfFilesInThisFolder(self, folderNameWithPath):
        return next(os.walk(folderNameWithPath))[self.FILES_IN_FOLDER]
    
    def getListOfSubfoldersInThisFolder(self, folderNameWithPath):
        return next(os.walk(folderNameWithPath))[self.SUBDIRECTORIES]
