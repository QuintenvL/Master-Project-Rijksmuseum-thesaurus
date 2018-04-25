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
    concept_schemes.add('http://hdl.handle.net/10934/RM0001.SCHEME.UNKOWN')
    schemeless_concepts = list_schemeless_concepts(dom)
    print('{} {} concepts without a concept scheme'
    .format(time(start), len(schemeless_concepts)))
    # inverse_hierarchy = create_inverse_hierarchy(dom)
    # print('{} extracted {} concepts with relations to other concepts'
    # .format(datetime.now() - startTime, len(inverse_hierarchy)))
    # differences = list_hierarchical_differences(inverse_hierarchy, dom)
    # print('{} found {} hierarchical differences'
    # .format(datetime.now() - startTime, len(differences)))
    # dom = add_concept_schemes(dom, concept_schemes)
    # print('{} added {} concept schemes to dom'
    # .format(datetime.now() - startTime, len(concept_schemes)))
    # dom = reconstruct_hierarchy(dom, concepts, differences)
    # print('{} added {} hierarchical differences to dom'
    # .format(datetime.now() - startTime, len(differences)))
    # write_dom_to_file(dom, transformed_file)
    # print('{} wrote dom to file {}'
    # .format(datetime.now() - startTime, transformed_file))
    # save_schemeless(schemeless_concepts, missing_file)
    # print('{} wrote concepts without scheme to file {}'
    # .format(datetime.now() - startTime, missing_file))
    # save_differences(differences, issue_file)
    # print('{} wrote hierarchical differences to file {}'
    # .format(datetime.now() - startTime, issue_file))

def time(start):
    return datetime.now() - start
# def reconstruct_hierarchy(dom, concepts, difference_lists):
#     root = dom.childNodes.item(0)
#
#     #TODO: see if we can only loop through difference_lists and retrieve the property_dict based on concept_id
#     for concept in root.childNodes:
#         if concept.nodeName == 'skos:ConceptScheme':
#             continue
#         if concept.nodeType == concept.ELEMENT_NODE:
#             concept_id = concept.attributes.items()[0][1]
#             property_dict = create_property_dict(concept.childNodes)
#             remove_list = []
#
#             # Each difference will be added to the root
#             for difference_list in difference_lists:
#                 #TODO: check if there is a clever way to deconstruct list
#                 concept_id = difference_list[0]
#                 h_label = difference_list[1]
#                 differences = difference_list[2]
#
#                 for difference in differences:
#                     # If the difference concept is missing the
#                     # difference, a new property node will be added to
#                     # the concept node that missed the relation property.
#                     if difference in concepts:
#                         if difference in property_dict[h_label]:
#                             dom = add_element(difference, h_label, dom)
#     return dom
#
# def add_element(difference, h_label, dom):
#     root = dom.childNodes.item(0)
#
#     for another_concept in root.childNodes:
#         if another_concept.nodeName == 'skos:ConceptScheme':
#             continue
#         if another_concept.nodeType == another_concept.ELEMENT_NODE:
#             another_concept_id = another_concept.attributes.items()[0][1]
#
#             if another_concept_id == difference:
#                 if h_label == 'skos:broader':
#                     new_node = dom.createElement('skos:narrower')
#                 elif h_label == 'skos:narrower':
#                     new_node = dom.createElement('skos:broader')
#                 elif h_label == 'skos:related':
#                     new_node = dom.createElement('skos:related')
#             another_concept.appendChild(new_node)
#             new_node.setAttribute('rdf:resource', concept_id)
#     return dom






def create_inverse_hierarchy(dom):
    # The inverse of every hierarchical skos relation is added to a dictionary:
    # {'http://concept.net/2': {'skos:broader': ['http://concept.net/1']}}
    hierarchy_dict = {}
    o_rdf = dom.childNodes.item(0)

    for o_concept in o_rdf.childNodes:
        for o_property in o_concept.childNodes:
            if (o_property.nodeType == o_property.ELEMENT_NODE
            and (o_property.nodeName == 'skos:broader'
            or o_property.nodeName == 'skos:narrower'
            or o_property.nodeName == 'skos:related')):
                o_concept_id = o_concept.attributes.items()[0][1]
                prop_name = o_property.nodeName
                prop_inv = inverse_property(prop_name)
                prop_attr = o_property.attributes.items()[0][1]

                if prop_attr not in hierarchy_dict:
                    hierarchy_dict[prop_attr] = {}
                    hierarchy_dict[prop_attr][prop_inv] = [o_concept_id]
                elif prop_inv not in hierarchy_dict[prop_attr]:
                    hierarchy_dict[prop_attr][prop_inv] = [o_concept_id]
                else:
                    hierarchy_dict[prop_attr][prop_inv].append(o_concept_id)
    return hierarchy_dict


def inverse_property(property_name):
    if property_name == 'skos:broader':
        return 'skos:narrower'
    elif property_name == 'skos:narrower':
        return 'skos:broader'
    else:
        return 'skos:related'


def list_hierarchical_differences(inverse_hierarchy, dom):
    root = dom.childNodes.item(0)
    list_of_differences = []

    # Iterate through all concepts listing hierarchical differences
    for concept in root.childNodes:
        if concept.nodeName == 'skos:ConceptScheme':
            continue
        if concept.nodeType == concept.ELEMENT_NODE:
            concept_id = concept.attributes.items()[0][1]
            properties = create_property_dict(concept.childNodes)

            # 1. Verify based upon the inverse hierarchy whether the
            # concept has all hierarchical properties it should have.
            if concept_id in inverse_hierarchy:
                h_properties = inverse_hierarchy[concept_id]
                diff = missing_properties(properties, h_properties)
    return list_of_differences

def missing_properties(properties, h_properties):
    hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']

    for h_label in hierarchy_labels:
        if h_label in properties and h_label in h_properties:
            difference = list(
                set(property_dict[h_label])
                - set(inverse_hierarchy[concept_id][h_label])
            )
            if difference != []:
                difference_list = [
                    concept_id, h_label, difference
                ]
    return difference_list

def create_property_dict(concept_properties):
    # Each property is stored in a dictionary with the name of the
    # property and its value.
    property_dict = {}

    for property in concept_properties:
        if property.nodeType == property.ELEMENT_NODE:
            # Properties with text nodes or other nodes and the
            # skos:topConceptOf nodes are excluded from the property
            # dictionary.
            if (property.hasChildNodes()
            or property.nodeName == 'skos:topConceptOf'):
                continue
            else:
                label = property.nodeName
                attribute_value = property.attributes.items()[0][1]
                if label in property_dict:
                    property_dict[label].append(attribute_value)
                else:
                    property_dict[label] = [attribute_value]
    return property_dict


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
