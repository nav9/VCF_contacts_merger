from vcf_parser import VCF
#from tests import commonFunctions
#from fileAndFolder import fileFolderOperations
#Each test case is designed to be a self-contained environment. 

class TestPhoneNumberDuplicate:
    def test_checkIfAllDuplicatesAreFound(self):        
        folderChosen = ''
        fileOps = None #not needed for this test
        contacts = [['BEGIN:VCARD', 'VERSION:2.1', 'N:;Somename1;;;', 'FN:Somename1', 'TEL;CELL:01111111111', 'TEL;HOME:5555555555', 'TEL;HOME:3333333333', 'TEL;HOME:04444444444', 'EMAIL;X-INTERNET:dummyemail1@domain.co.in', 'END:VCARD'], 
                    ['BEGIN:VCARD', 'VERSION:2.1', 'N:;Somename5;;;', 'FN:Somename5', 'TEL;CELL:3333333333', 'END:VCARD'], 
                    ['BEGIN:VCARD', 'VERSION:2.1', 'N:;Somename1;;;', 'FN:Somename1', 'TEL;CELL:01111111111', 'TEL;CELL:+912222222222', 'TEL;HOME:3333333333', 'EMAIL;X-INTERNET:dummyemail1@domain.co.in', 'END:VCARD'], 
                    ['BEGIN:VCARD', 'VERSION:2.1', 'N:;Somename1;;;', 'FN:Somename1', 'TEL;CELL;PREF:01111111111', 'TEL;VOICE:5555555555', 'TEL;VOICE:3333333333', 'TEL;HOME:04444444444', 'END:VCARD'], 
                    ['BEGIN:VCARD', 'VERSION:2.1', 'N:;Somename4;;;', 'FN:Somename4', 'TEL;CELL:3333333333', 'END:VCARD'], 
                    ['BEGIN:VCARD', 'VERSION:2.1', 'N:Somename2;Somename1;Some Name3;;', 'FN:Somename1 Some Name3 Somename2', 'TEL;CELL:1111111111', 'TEL;WORK:3333333333', 'EMAIL;PREF:dummyemail1@domain.co.in', 'END:VCARD'], ['BEGIN:VCARD', 'VERSION:2.1', 'N:;SamePerson;;;', 'FN:SamePerson', 'TEL;CELL;PREF:01111111111', 'TEL;CELL:+912222222222', 'EMAIL;X-INTERNET:dummyemail1@domain.co.in', 'END:VCARD'], ['BEGIN:VCARD', 'VERSION:2.1', 'N:;Somename1;;;', 'FN:Somename1', 'TEL;CELL:01111111111', 'TEL;CELL:+912222222222', 'TEL;HOME:3333333333', 'EMAIL;X-INTERNET:dummyemail1@domain.co.in', 'END:VCARD'], ['BEGIN:VCARD', 'VERSION:2.1', 'N:;SamePerson_internet;;;', 'FN:SamePerson_internet', 'TEL;CELL:+912222222222', 'END:VCARD']
                ]
        vcf_merger = VCF(fileOps, folderChosen)
        vcf_merger.allContacts = contacts
        numDuplicates = vcf_merger.searchForDuplicateContactsBasedOnPhoneNumber()
        assert numDuplicates == 1 #all the contacts provided belong to one person who has multiple phone numbers, so only 1 duplicate should be detected
