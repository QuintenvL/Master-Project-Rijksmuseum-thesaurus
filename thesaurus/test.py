test1 = 'http://hdl.handle.net/10934/RM0001.THESAU.903'
test2 = 'http://vocab.getty.edu/aat/300011914'

import re


print re.findall(r'\b\d+\b', test1)[-1]
print re.findall(r'\b\d+\b', test2)[-1]

a_label = 'skos:broader'
print a_label[5:]