#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parsing the AAT

Script which collects and analyses concepts of the AAT.
"""

__author__ = "Quinten van Langen"
__version__ = "1.0.0"
__license__ = "cc0-1.0"


import urllib
import os
import xml.etree.ElementTree as ET
import pandas as pd
from xml.dom.minidom import parse
import csv
import pickle
from datetime import datetime
from analyse import *

# Dictionary of prefixes 
prefixes = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 
            'gvp': 'http://vocab.getty.edu/ontology#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'skos': 'http://www.w3.org/2004/02/skos/core#', 
            'skosxl': 'http://www.w3.org/2008/05/skos-xl#'}

def main():
    start = datetime.now()
    os.chdir('out')
    print 'Set a maximum amount of concepts to be retrieved:'
    set_maximum = raw_input()
    print('{} Set the maximum to {}'
    .format(time(start), set_maximum))
    print('Please provide a name for the output files (e.g. example_analyse.xlsx) (only "example" is replaced by the input)')
    output_name = raw_input()
    dict_file = '../out/AAT/{}_dictionary.pkl'.format(output_name)
    analyse_file = '../out/AAT/{}_analyse.xlsx'.format(output_name)

    # Script to gather AAT concepts by downloading and processing RDF files
    processed_concepts = []
    list_of_concepts = ['http://vocab.getty.edu/aat/300192974'] # Contains the start concept
    concept_dict = {}
    for a_concept in list_of_concepts:
        try:
            if len(concept_dict) > int(set_maximum) - 1: # Specifies the amount of concepts returned
                break
            if a_concept in processed_concepts: # Skips concepts already gathered
                continue
            if len(concept_dict) % 100 == 0 and len(concept_dict) != 0: # Shows running time and total amount after gathering 100 concepts
                print('{} Gathered {} concepts'
                .format(time(start), len(concept_dict)))
        #Opens the download URL and checks if it is responsing
            website = a_concept + '.rdf'
            urllib.urlretrieve (website, "file.rdf")
            if urllib.urlopen(website).code != 200:
                continue
        #Gather all the wanted information of a concept and store it a dictionary
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
                # if 'http://vocab.getty.edu/aat/300264091' not in new_list and concept_id != 'http://vocab.getty.edu/aat/300264091': # Specify the material facet
                #     continue
                if '{http://www.w3.org/2004/02/skos/core#}exactMatch' in properties_list:
                    match = concept.findall('skos:exactMatch', prefixes)
                    for i in match:
                        for j in i:
                            for labels in concept:
                                if labels.tag not in properties_list:
                                    properties_list.append(labels.tag)
                            concept_dict[concept_id], list_of_properties = gather_properties(j)
                            short_concept_id = re.findall(r'\b\d+\b', concept.attrib.items()[0][1])[-1]
                            concept_dict[concept_id]['id'] = short_concept_id
                            concept_dict[concept_id]['labels'] = properties_list
                            list_of_concepts += list_of_properties[0] + list_of_properties[1] + list_of_properties[2]
                else:
                    concept_dict[concept_id], list_of_properties = gather_properties(concept)
                    short_concept_id = re.findall(r'\b\d+\b', concept.attrib.items()[0][1])[-1]
                    concept_dict[concept_id]['id'] = short_concept_id
                    concept_dict[concept_id]['labels'] = properties_list
                    list_of_concepts += list_of_properties[0] + list_of_properties[1] + list_of_properties[2]
        except IOError:
            pass
            continue        

    print('{} Finished collecting {} concepts'
    .format(time(start), len(concept_dict)))

    # Write all properties to a file
    output = open(dict_file, 'wb')
    pickle.dump(concept_dict, output)
    output.close() 
    print('{} Saved the properties of all concepts to file {}'
    .format(time(start), dict_file))

    write_analyse_file(concept_dict, analyse_file)
    print('{} write analyse results to the file {}'
    .format(time(start), analyse_file))   

#Function to gather properties of a AAT concept and return it in a dictionary
def gather_properties (concept):
    dict_of_properties = {}
    list_of_properties = []
    types = ['skos:broader', 'skos:narrower', 'skos:related', 'prefLabel', 'altLabel']
    for i in types:
        if 'skos' not in i:
            the_query = 'skos:' + i
        else:
            the_query = i
        property_list = concept.findall(the_query, prefixes)
        if types.index(i) <= 2:
            another_property_list = relation_processing(property_list, 'yes')
            property_list = relation_processing(property_list, 'no')
        else:
            property_list = label_processing(property_list)
            another_property_list = property_list
        dict_of_properties[i] = another_property_list
        list_of_properties.append(property_list)
    return dict_of_properties, list_of_properties

#Function to gather labels and their language in a dictionary
def label_processing(list):
    return_list = []
    for i in list:
        concept_dict = {}
        if i.attrib.values() != []:
            language = i.attrib.values()[0]
        else:
            language = 'unknown'
        label = i.text.encode('utf-8')
        concept_dict['language'] = language
        concept_dict['label'] = label
        return_list.append(concept_dict)
    return return_list

#Function to gather all relations 
def relation_processing(list, extra):
    return_list = []
    for i in list:
        if extra == 'yes':
            relation = re.findall(r'\b\d+\b', i.attrib.items()[0][1])[-1]
        else:
            relation = i.attrib.values()[0]
        return_list.append(relation)
    return return_list

def time(start):
    return datetime.now() - start

def write_analyse_file(dict, file):
    dict = determine_depth(dict)
    list = []
    for i in dict:
        list.append(dict[i])
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    reference_dict, reference_list = reference_analyse(list)
    df_full = pd.DataFrame.from_dict(list)
    df_full.to_excel(writer, sheet_name='Full')
    reference_df = pd.DataFrame(reference_list, index=['Broader', 'Narrower', 'Related'])
    reference_df.to_excel(writer, sheet_name='Reference1')
    reference_df2 = pd.DataFrame(reference_dict.items(), columns=['B-N-R', '#'])
    reference_df2 = reference_df2.sort_values(by=['#'], ascending=False)
    reference_df2.to_excel(writer, sheet_name='Reference2')
    dict1, dict2, dict3 = label_analyse(list)
    label_df = pd.DataFrame.from_dict(dict1, orient='index')
    label_df.to_excel(writer, sheet_name='Labels')
    label_df2 = pd.DataFrame.from_dict(dict2, orient='index')
    label_df2.to_excel(writer, sheet_name='Labels2')
    label_df3 = pd.DataFrame.from_dict(dict3, orient='index')
    label_df3.to_excel(writer, sheet_name='Labels3')


    # Write all information of a concept to a csv file
    # writer = csv.writer(open('AAT_concepts.csv','wb'))
    # headers = ['id']
    # headers += concept_dict[concept_id].keys()
    # writer.writerow(headers)
    # for key, value in concept_dict.iteritems():
    #     ln = [key]
    #     for ik, iv in value.iteritems():
    #         ln.append(iv)
    #     writer.writerow(ln)

    
if __name__ == "__main__":
    main()