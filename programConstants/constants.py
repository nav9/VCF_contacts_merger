import os

class GlobalConstants:
    duplicateFilesFolder = os.path.join("duplicateFilesFolder", "") #The quotes at the end add an OS-specific folder slash
    previouslySelectedFolderForDuplicatesCheck = "previouslySelectedFolder.txt" #store the folder name of the folder that was last selected, so that the User does not have to re-navigate from the beginning
    FIRST_POSITION_IN_LIST = 0
    VCF_EXTENSION = '.vcf'
    NUMBER_OF_TEL_END_DIGITS = 8 #number of digits at the end of the telephone number to consider for matching with phone numbers of other contacts
    COLON_DELIMITER = ":"
    SEMICOLON_DELIMITER = ";"

class Layout:#these constants are kept here in case any functions outside menus.py needs access
    NEXT_BUTTON = 'Next contact >'
    PREV_BUTTON = '< Previous contact'
    SAVE_BUTTON = 'Save'
    CONTACTS_DISPLAY_TEXTFIELD = 'contactsDisplay'
    DUPLICATES_DISPLAY_TEXTFIELD = 'duplicatesDisplay'
    COLOR_GREY = 'grey'
    LEFT_JUSTIFY = 'left'
    RIGHT_JUSTIFY = 'right'

class Properties:#property names present in a VCard https://en.wikipedia.org/wiki/VCard#toc-Properties
    BEGIN = 'BEGIN'
    VCARD = 'VCARD'
    EMAIL = 'EMAIL'
    END = 'END'
    FN = 'FN' #formatted name 
    N = 'N' #name
    NAME = 'NAME'
    TEL = 'TEL'
    