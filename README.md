![Alt text](gallery/GUI1.png?raw=true "The VCF duplicate examiner GUI")  
  
# VCF_contacts_merger
A simple tool to help merge multiple Virtual Contact File (VCF) files. These are the vCard files used in smartphones.  
It automatically finds unique contacts and displays duplicate contacts for you to inspect.  
Contacts are analyzed for similarity based on the last few characters in the rows that store phone numbers.
  
# Prerequisite  
Do the following pip install before running the program:
`pip install loguru textwrap`
  
# Run  
As a general precaution, keep backups of your contact files even after merging them.  
Run the program using: `python main.py`
  
# Other resources
* Wikipedia [info on VCF files](https://en.wikipedia.org/wiki/VCard).
* [Another tool](https://pypi.org/project/vcardtools/) for interactively merging VCF files.
* [A library](https://eventable.github.io/vobject/) for processing VCF data. This project appears to no longer be maintained. It could be installed using `pip install vobject` and used with `import vobject`.
* Dummy [VCF data](https://gist.github.com/kaltekar/2919260).

# To run the tests  
It's not necessary to use the exact version of pytest mentioned below. The version is mentioned only to indicate which version was used at the time.  
`pip3 install pytest=7.4.2`    
Use `pytest` at the commandline to run the test cases. Do this in the root program directory.  
To run `pytest` for a specific test file only, run it like this: `pytest tests/test_filename.py`.  
To run `pytest` for a specific test function in a test file, run it like this: `pytest tests/test_filename.py -k 'test_functionName'`.  
To see the captured output of passed tests, use `pytest -rP`. For failed tests, use `pytest -rx`. All outputs will be shown with `pytest -rA`.  

# TODO
* Add an option to remove photos from contacts
* Add an option to remove contacts that have no phone number mentioned

[![Donate](https://raw.githubusercontent.com/nav9/VCF_contacts_merger/main/gallery/thankYouDonateButton.png)](https://nrecursions.blogspot.com/2020/08/saying-thank-you.html)  
