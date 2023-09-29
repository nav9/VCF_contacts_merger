import os

class GlobalConstants:
    VCF_EXTENSION = '.vcf'
    DEFAULT_SAVE_FILENAME = "mergedUniqueContacts"
    PROGRAM_STATE_SAVE_FILENAME = "tempContacts_doNotEdit.pickle"
    #duplicateFilesFolder = os.path.join("duplicateFilesFolder", "") #The quotes at the end add an OS-specific folder slash
    previouslySelectedFolderForDuplicatesCheck = "previouslySelectedFolder.txt" #store the folder name of the folder that was last selected, so that the User does not have to re-navigate from the beginning
    FIRST_POSITION_IN_LIST = 0  
    SECOND_POSITION_IN_LIST = 1  
    NUMBER_OF_TEL_END_DIGITS = 8 #number of digits at the end of the telephone number to consider for matching with phone numbers of other contacts
    COLON_DELIMITER = ":"
    SEMICOLON_DELIMITER = ";"
    SLEEP_SECONDS = 0.03 
    FORWARD = 1 #list index update direction
    BACKWARD = -1 #list index update direction
    NEWLINE = '\n'
    MAX_LENGTH_OF_ERROR = 300 #maximum number of characters of error to show in GUI

class Layout:#these constants are kept here in case any functions outside menus.py needs access
    WINDOW_WAIT_TIMEOUT_MILLISECOND = 100 #the amount of time the window waits for user input        
    NEXT_BUTTON = 'Next contact >'
    PREV_BUTTON = '< Previous contact'
    SAVE_BUTTON = 'Save'
    EXPLANATION_BUTTON = 'Explanation'
    YES_BUTTON = 'Yes'
    NO_BUTTON = 'No'
    
    CONTACTS_DISPLAY_TEXTFIELD = '- contactsDisplay -'
    DUPLICATES_DISPLAY_TEXTFIELD = '- duplicatesDisplay -'
    CONTACTS_COMPLETED_TEXT = '- contactsCompleted -'
    #HELP_INFO_MULTILINE = '- help info -'
    COLOR_GREY = 'grey'
    LEFT_JUSTIFY = 'left'
    RIGHT_JUSTIFY = 'right'
    CENTER_JUSTIFY = 'center'  

class Properties:#property names present in a VCard https://en.wikipedia.org/wiki/VCard#toc-Properties
    BEGIN = 'BEGIN'
    VCARD = 'VCARD'
    EMAIL = 'EMAIL'
    END = 'END'
    FN = 'FN' #formatted name 
    N = 'N' #name
    NAME = 'NAME'
    TEL = 'TEL'
    