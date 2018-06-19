#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reconstruct SKOS

Script which analyses and reconstructs a SKOS hierarchy.
"""

__author__ = "Quinten van Langen"
__version__ = "1.0.0"
__license__ = "cc0-1.0"


import os
import csv
import pandas as pd
import pickle
from xml.dom.minidom import parse
from shutil import copyfile
from datetime import datetime
from analyse import *


def main():
    start = datetime.now()
    os.chdir('data')
    print('Please provide the name of the input file (e.g. example.rdf):')
    source_file = raw_input()
    print('Please provide a name for the output files (e.g. example_transformed.rdf) (only "example" is replaced by the input)')
    output_name = raw_input()
    transformed_file = '../out/{}_transformed.rdf'.format(output_name)
    issue_file = '../out/{}_differences.csv'.format(output_name)
    typeless_file = '../out/{}_typeless.csv'.format(output_name)
    analyse_file = '../out/{}_analyse.xlsx'.format(output_name)
    dict_file = '../out/{}_dictionary.pkl'.format(output_name)

    print('{} started analysis'.format(time(start)))
    dom = parse(source_file)
    print('{} parsed {}'.format(time(start), source_file))
    concepts = list_concepts(dom)
    print('{} analyzing {} concepts'
    .format(time(start), len(concepts)))
    concept_schemes = referenced_concept_schemes(dom)
    print('{} identified {} concept schemes'
    .format(time(start), len(concept_schemes)))
    # Add unknown scheme, for concepts without a type
    concept_schemes.append('http://hdl.handle.net/10934/RM0001.SCHEME.UNKOWN')
    schemeless_concepts = list_schemeless_concepts(dom)
    print('{} {} concepts without a concept scheme'
    .format(time(start), len(schemeless_concepts)))

    missing_references = missing_outward_references(dom)
    missing_references = restructure_missing_references(missing_references)
    print('{} found {} hierarchical inconsistencies'
    .format(time(start), len(missing_references)))

    undefined_concepts = undefined_concept_references(dom)
    print('{} found {} references to undefined concepts'
    .format(time(start), len(undefined_concepts)))

    new_dom = dom.cloneNode(dom)
    new_dom = add_concept_schemes(new_dom, concept_schemes)
    print('{} added {} concept schemes to dom'
    .format(time(start), len(concept_schemes)))
    new_dom = fix_loose_references(new_dom, missing_references)
    print('{} added the {} missing references to file{}'
    .format(time(start), len(missing_references), transformed_file))
    new_dom = remove_undefined_references(new_dom, undefined_concepts)
    print('{} removed the {} undefined references from file {}'
    .format(time(start), len(undefined_concepts), transformed_file))

    topconcepts = find_top_concepts(new_dom)
    print('{} found {} concepts without broader concepts'
    .format(time(start), len(topconcepts)))

    schemes_dict = find_all_schemes(new_dom, 'no')
    print('{} created a dictionary of schemes'
    .format(time(start)))

    new_dom = add_top_concepts(new_dom, topconcepts, schemes_dict)
    print('{} added topconcept nodes to file {}'
    .format(time(start), transformed_file))

    the_properties = all_properties(new_dom, 'yes')
    print('{} created property dictionary for each concept'
    .format(time(start)))


    write_dom_to_file(new_dom, transformed_file)
    print('{} wrote new dom to file {}'
    .format(time(start), transformed_file))
    save_schemeless(schemeless_concepts, typeless_file)
    print('{} wrote concepts without scheme to file {}'
    .format(time(start), typeless_file))
    save_differences(missing_references, undefined_concepts, issue_file)
    print('{} wrote hierarchical differences to file {}'
    .format(time(start), issue_file))

    write_analyse_file(the_properties, analyse_file)
    print('{} write analyse results to the file {}'
    .format(time(start), analyse_file))

    output = open(dict_file, 'wb')
    properties_dict = {}
    for concept in the_properties:
        the_id = concept['id']
        properties_dict[the_id] = concept
    pickle.dump(properties_dict, output)
    output.close()
    print('{} Saved the properties of each concept to file {}'
    .format(time(start), dict_file))


def add_concept_schemes(dom, concept_schemes):
    # Add missing skos:ConceptScheme nodes to the root
    root = dom.childNodes.item(0)

    for scheme in concept_schemes:
        scheme_node = dom.createElement('skos:ConceptScheme')
        root.appendChild(scheme_node)
        scheme_node.setAttribute('rdf:about', scheme)
        concept_node = dom.createElement('dct:title')
        scheme_node.appendChild(concept_node)
        concept_node.setAttribute('xml:lang', 'nl')
        if scheme == 'http://hdl.handle.net/10934/RM0001.SCHEME.UNKOWN':
            text_node = dom.createTextNode('Scheme Unknown')
        else:
            text_node = dom.createTextNode(scheme[42:])
        concept_node.appendChild(text_node)
    return dom

def remove_reference(dom, reference):
    # Remove a reference from a concept
    c1 = reference[2]
    c2 = reference[0]
    if c1 == c2:
        relation = inverse_property(reference[1])
    else:
        c1 = reference[0]
        c2 = reference[2]
        relation = reference[1]
    c1 = get_concept(dom, c1)
    if c1 is not None:
        property_node = get_relation_property(c1, relation, c2)
        c1.removeChild(property_node)
    return dom


def remove_undefined_references(dom, references):
    # remove all undefined references
    for reference in references:
        dom = remove_reference(dom, reference)
    return dom


def fix_loose_references(dom, references):
    # A fix of the loose references
    for reference in references:
        c1 = reference[0]
        relation = reference[1]
        c2 = reference[2]
        if c1 == c2:
            dom = remove_reference(dom, reference)
        else:
            c1 = get_concept(dom, c1)
            if c1 is not None:
                new_node = dom.createElement(relation)
                c1.appendChild(new_node)
                new_node.setAttribute('rdf:resource', c2)
    return dom

def add_top_concepts(dom, concepts, schemes):
    # Add the topconcept nodes to the concepts without broader concepts and to the conceptscheme nodes
    for concept in concepts:
        concept_id = concept
        the_schemes = schemes[concept_id]
        concept = get_concept(dom, concept)
        if the_schemes == []:
            the_schemes.append('http://hdl.handle.net/10934/RM0001.SCHEME.UNKOWN')
        for scheme in the_schemes:
            new_node = dom.createElement('skos:topConceptOf')
            concept.appendChild(new_node)
            new_node.setAttribute('rdf:resource', scheme)
            scheme = get_concept_scheme(dom, scheme)
            extra_node = dom.createElement('skos:hasTopConcept')
            scheme.appendChild(extra_node)
            extra_node.setAttribute('rdf:resource', concept_id)
    return dom



def save_schemeless(schemeless_concepts, typeless_file):
    # Each typeless concept is written to a csv file
    a_file  = open(typeless_file, "wb")
    the_writer = csv.writer(a_file)
    for schemeless in schemeless_concepts:
        the_writer.writerow([schemeless])
    a_file.close()


def save_differences(list1, list2, issue_file):
    # Each difference is written to a csv file
    header_list = ['concept 1', 'type of relation', 'concept 2']
    a_file  = open(issue_file, "wb")
    writer = csv.writer(a_file)
    writer.writerow(header_list)
    for difference in list1:
        writer.writerow(difference)
    writer.writerow(['-','-','-'])
    for difference in list2:
        writer.writerow(difference)
    a_file.close()


def write_dom_to_file(dom, file):
    # Write a dom to a XML file
    xml_file = open(file, "w")
    xml_file.write(dom.toprettyxml().encode("utf-8"))
    xml_file.close()

def write_analyse_file(list, file):
    # Write all analyses to a file
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
    matches_dict = matches_analyse(list)
    matches_df = pd.DataFrame(matches_dict.items(), columns=['Matches', '#'])   
    matches_df.to_excel(writer, sheet_name='Matches')
    type_dict = type_analyse(list)
    type_df = pd.DataFrame.from_dict(type_dict, orient='index')
    type_df.to_excel(writer, sheet_name='Types')

if __name__ == "__main__":
    main()
