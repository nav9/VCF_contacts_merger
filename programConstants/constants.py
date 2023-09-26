import os

class GlobalConstants:
    duplicateFilesFolder = os.path.join("duplicateFilesFolder", "") #The quotes at the end add an OS-specific folder slash
    previouslySelectedFolderForDuplicatesCheck = "previouslySelectedFolder.txt" #store the folder name of the folder that was last selected, so that the User does not have to re-navigate from the beginning
    EVENT_CANCEL = 'Cancel'
    EVENT_EXIT = 'Cancel'
    YES_BUTTON = 'Yes'
    NO_BUTTON = 'No'
    FIRST_POSITION_IN_LIST = 0
    VCF_EXTENSION = '.vcf'
    NUMBER_OF_TEL_END_DIGITS = 8 #number of digits at the end of the telephone number to consider for matching with phone numbers of other contacts
    COLON_DELIMITER = ":"
    SEMICOLON_DELIMITER = ";"

class Properties:#property names present in a VCard https://en.wikipedia.org/wiki/VCard#toc-Properties
    BEGIN = 'BEGIN'
    VCARD = 'VCARD'
    EMAIL = 'EMAIL'
    END = 'END'
    FN = 'FN' #formatted name 
    N = 'N' #name
    NAME = 'NAME'
    TEL = 'TEL'
    