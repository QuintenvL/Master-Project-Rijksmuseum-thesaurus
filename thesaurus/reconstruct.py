#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reconstruct SKOS

Script which analyses and reconstructs a SKOS hierarchy.
"""

__author__ = "Quinten van Langen"
__version__ = "0.2.0"
__license__ = "cc0-1.0"


import os
import csv
from xml.dom.minidom import parse
from shutil import copyfile
from datetime import datetime
from analyse import *


def main():
    start = datetime.now()
    os.chdir('data')
    source_file = 'rma-skos-materials.rdf'
    transformed_file = '../out/full_transformed.rdf'
    issue_file = '../out/full_differences.csv'
    missing_file = '../out/full_missing.csv'

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
    print('{} found {} hierarchical inconsistencies'
    .format(time(start), len(missing_references)))
    undefined_concepts = undefined_concept_references(dom)
    print('{} found {} references to undefined concepts'
    .format(time(start), len(concept_schemes)))
    #TODO: split all analysis routines from script into smaller defenitions
    new_dom = dom.cloneNode(dom)
    print(new_dom)
    new_dom = add_concept_schemes(new_dom, concept_schemes)
    print('{} added {} concept schemes to dom'
    .format(time(start), len(concept_schemes)))
    #TODO: write code removing loose references and missing hierarchical references
    # new_dom = reconstruct_hierarchy(new_dom, concepts, differences)
    # print('{} added {} hierarchical differences to dom'
    # .format(datetime.now() - startTime, len(differences)))
    write_dom_to_file(new_dom, transformed_file)
    print('{} wrote new dom to file {}'
    .format(time(start), transformed_file))
    save_schemeless(schemeless_concepts, missing_file)
    print('{} wrote concepts without scheme to file {}'
    .format(time(start), missing_file))
    #TODO: save all results of analysis
    save_differences(missing_references, issue_file)
    print('{} wrote hierarchical differences to file {}'
    .format(time(start), issue_file))


def time(start):
    return datetime.now() - start


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


def save_schemeless(schemeless_concepts, missing_file):
    # Each typeless concept is written to a csv file
    b_file  = open(missing_file, "wb")
    the_writer = csv.writer(b_file)
    for schemeless in schemeless_concepts:
        the_writer.writerow([schemeless])
    b_file.close()


def save_differences(list_of_differences, issue_file):
    # Each difference is written to a csv file
    header_list = ['concept 1', 'type of relation', 'concept 2']
    d_file  = open(issue_file, "wb")
    writer = csv.writer(d_file)
    writer.writerow(header_list)
    for difference in list_of_differences:
        writer.writerow(difference)
    d_file.close()


def write_dom_to_file(dom, file):
    # Write a dom to a XML file
    xml_file = open(file, "w")
    xml_file.write(dom.toprettyxml().encode("utf-8"))
    xml_file.close()


if __name__ == "__main__":
    main()
