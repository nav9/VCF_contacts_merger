![Alt text](gallery/GUI1.png?raw=true "The VCF duplicate examiner GUI")  
  
# VCF_contacts_merger
A simple tool to help merge multiple Virtual Contact File (VCF) files. These are the vCard files used in smartphones.  
It automatically finds unique contacts and displays duplicate contacts for you to inspect.  
Contacts are analyzed for similarity based on the last few characters in the rows that store phone numbers.
  
# Prerequisite  
Do the following pip install before running the program:
`pip install loguru textwrap`
  
# Run
`python main.py`
  
# Other resources
* Wikipedia [info on VCF files](https://en.wikipedia.org/wiki/VCard).
* [Another tool](https://pypi.org/project/vcardtools/) for interactively merging VCF files.
* [A library](https://eventable.github.io/vobject/) for processing VCF data. This project appears to no longer be maintained. It could be installed using `pip install vobject` and used with `import vobject`.
* Dummy [VCF data](https://gist.github.com/kaltekar/2919260).
