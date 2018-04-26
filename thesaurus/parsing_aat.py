'''
Created on 6 apr. 2018

@author: Gebruiker
'''
import urllib
import os
import xml.etree.ElementTree as ET
import csv
from datetime import datetime

startTime = datetime.now()
midTime = startTime

os.chdir('Outputs')
# Dictionary of prefixes 
prefixes = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 
            'gvp': 'http://vocab.getty.edu/ontology#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'skos': 'http://www.w3.org/2004/02/skos/core#', 
            'skosxl': 'http://www.w3.org/2008/05/skos-xl#'}

# Function to gather properties of a AAT concept and return it in a list
def properties (concept):
    list_of_properties = []
    types = ['broader', 'narrower', 'related', 'prefLabel', 'altLabel']
    for i in types:
        the_query = 'skos:' + i
        property_list = concept.findall(the_query, prefixes)
        if types.index(i) <= 2:
            property_list = relation_processing(property_list)
        else:
            property_list = label_processing(property_list)
        list_of_properties.append(property_list)
    return list_of_properties

#Function to gather properties of a AAT concept and return it in a dictionary
def dict_properties (concept):
    dict_of_properties = {}
    types = ['broader', 'narrower', 'related', 'prefLabel', 'altLabel']
    for i in types:
        the_query = 'skos:' + i
        property_list = concept.findall(the_query, prefixes)
        if types.index(i) <= 2:
            property_list = relation_processing(property_list)
        else:
            property_list = label_processing(property_list)
        dict_of_properties[i] = property_list
    return dict_of_properties

#Function to gather labels and their language in a dictionary
def label_processing(list):
    return_dict = {}
    for i in list:
        if i.attrib.values() != []:
            language = i.attrib.values()[0]
        else:
            language = 'unknown'
        label = i.text.encode('utf-8')
        return_dict[label] = language
    return return_dict 

#Function to gather all relations 
def relation_processing(list):
    return_list = []
    for i in list:
        relation = i.attrib.values()[0]
        return_list.append(relation)
    return return_list
# Script to gather AAT concepts by downloading and processing RDF files
processed_concepts = []
list_of_concepts = ['http://vocab.getty.edu/aat/300192974'] # Contains the start concept
# 'http://vocab.getty.edu/aat/300011816'
concept_dict = {}
for a_concept in list_of_concepts:
#     if len(concept_dict) > 99: # Specifies the amount of concepts returned
#         break
    if a_concept in processed_concepts: # Skips concepts already gathered
        continue
    if len(concept_dict) % 100 == 0 and len(concept_dict) != 0: # Shows running time and total amount after gathering 100 concepts
        print "Amount of gathered concepts =", len(concept_dict)
        print 'Midtime = ', datetime.now() - midTime
        midTime = datetime.now()
#Opens the download URL and checks if it is responsing
    website = a_concept + '.rdf'
    urllib.urlretrieve (website, "file.rdf")
    if urllib.urlopen(website).code != 200:
        print urllib.urlopen(website).code
        break
#Gather all the wanted information of a concept and stores it a dictionary
    tree = ET.parse('file.rdf')
    root = tree.getroot()
    concepts = root.findall('gvp:Subject', prefixes)
    for concept in concepts:
        concept_id = concept.attrib.values()[0]
        processed_concepts.append(concept_id)
        properties_list = []
        for labels in concept:
            if labels.tag not in properties_list:
                properties_list.append(labels.tag)
        generic_broaders = concept.findall('gvp:broaderExtended', prefixes)
        new_list = []
        for i in generic_broaders:
            new_list.append(i.attrib.values()[0])
        if 'http://vocab.getty.edu/aat/300264091' not in new_list and concept_id != 'http://vocab.getty.edu/aat/300264091': # Specify the material facet
            continue
        if '{http://www.w3.org/2004/02/skos/core#}exactMatch' in properties_list:
            match = concept.findall('skos:exactMatch', prefixes)
            for i in match:
                for j in i:
                    for labels in concept:
                        if labels.tag not in properties_list:
                            properties_list.append(labels.tag)
                    broader, narrower, related, preflabel, altlabel = properties(j)
                    concept_dict[concept_id] = dict_properties(j)
                    concept_dict[concept_id]['labels'] = properties_list
                    list_of_concepts += broader + narrower + related
        else:    
            broader, narrower, related, preflabel, altlabel = properties(concept)
            concept_dict[concept_id] = dict_properties(concept)
            concept_dict[concept_id]['labels'] = properties_list
            list_of_concepts += broader + narrower + related
            
# Write all information of a concept to a csv file
writer = csv.writer(open('AAT_concepts.csv','wb'))
headers = ['id']
headers += concept_dict[concept_id].keys()
writer.writerow(headers)
for key, value in concept_dict.iteritems():
    ln = [key]
    for ik, iv in value.iteritems():
        ln.append(iv)
    writer.writerow(ln)

print 'Total time = ', datetime.now() - startTime
print 'Total amount of concepts = ', len(concept_dict)
    

