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
from sets import Set


def main():
    startTime = datetime.now()
    os.chdir('data')
    source_file = 'rma-skos-thesaurus.rdf'
    transformed_file = '../out/full_transformed.rdf'
    issue_file = '../out/full_differences.csv'
    missing_file = '../out/full_missing.csv'

    print('{} started analysis'.format(datetime.now() - startTime))
    dom = parse(source_file)
    print('{} parsed {}'.format(datetime.now() - startTime, source_file))
    concept_identifiers = list_concepts(dom)
    print('{} analyzing {} concepts'
    .format(datetime.now() - startTime, len(concept_identifiers)))
    concept_schemes = list_concept_schemes(dom)
    print('{} identified {} concept schemes'
    .format(datetime.now() - startTime, len(concept_schemes)))
    inverse_hierarchy = create_inverse_hierarchy(dom)
    print('{} extracted {} concepts with relations to other concepts'
    .format(datetime.now() - startTime, len(inverse_hierarchy)))
    schemeless_concepts = list_schemeless_concepts(dom)
    print('{} {} concepts without a concept scheme'
    .format(datetime.now() - startTime, len(schemeless_concepts)))
    dom = add_concept_schemes(dom, concept_schemes)
    print('{} added {} concept schemes to dom'
    .format(datetime.now() - startTime, len(concept_schemes)))
    write_dom_to_file(dom, transformed_file)
    print('{} wrote dom to file {}'
    .format(datetime.now() - startTime, transformed_file))
    #dom = create_valid_hierarchy(dom)
    #process_results(dom)
    #print('{} saved dom to file {}'.format(datetime.now() - startTime, transformed_file))


def list_schemeless_concepts(dom):
    schemeless_concepts = []
    root = dom.childNodes.item(0)

    for concept in root.childNodes:
        if concept.nodeName == 'skos:ConceptScheme':
            continue
        if concept.nodeType == concept.ELEMENT_NODE:
            concept_id = concept.attributes.items()[0][1]
            concept_properties = concept.childNodes
            property_names = []

            for property in concept_properties:
                property_names.append(property.nodeName)
            if 'skos:inScheme' not in property_names:
                schemeless_concepts.append(concept_id)
    return schemeless_concepts


# def create_valid_hierarchy(dom):
#     root = dom.childNodes.item(0)
#
#     for concept in root.childNodes:
#         # Ignore concept schemes just added to dom
#         if concept.nodeName == 'skos:ConceptScheme':
#             continue
#         if concept.nodeType == concept.ELEMENT_NODE:
#             concept_id = concept.attributes.items()[0][1]
#             concept_properties = concept.childNodes
#             property_dict = {}
#
#             # Each property of a concept is stored in a dictionary with the name of the property and its value
#             for property in concept_properties:
#                 if property.nodeType == property.ELEMENT_NODE:
#                     # Properties with text nodes or other nodes and the skos:topConceptOf nodes are excluded from the property dictionary
#                     if (property.hasChildNodes()
#                     or property.nodeName == 'skos:topConceptOf'):
#                         continue
#                     else:
#                         label = property.nodeName
#                         attr_value = property.attributes.items()[0][1]
#                         if label in property_dict:
#                             property_dict[label].append(attr_value)
#                         else:
#                             property_dict[label] = [attr_value]
#                         # All concepts without the skos:inScheme property are added to the list of schemeless concepts
#                         if 'skos:inScheme' not in property_dict:
#                             typeless_concepts.append(concept_id)
#             #         # With the use of a list of relation property labels, the script runs over every relation
#     return dom


# full_list_of_differences = []
# typeless_concepts = []

def list_concepts(dom):
    concept_identifiers = []
    o_rdf = dom.childNodes.item(0)

    # Create a list with the id's of the concepts
    for o_concept in o_rdf.childNodes:
        if o_concept.nodeType == o_concept.ELEMENT_NODE:
            o_concept_id = o_concept.attributes.items()[0][1]
            concept_identifiers.append(o_concept_id)
    return concept_identifiers


def list_concept_schemes(dom):
    unknown_scheme = 'http://hdl.handle.net/10934/RM0001.SCHEME.UNKOWN'
    concept_schemes = Set([unknown_scheme])
    o_rdf = dom.childNodes.item(0)

    for o_concept in o_rdf.childNodes:
        for o_property in o_concept.childNodes:
            if (o_property.nodeType == o_property.ELEMENT_NODE
            and o_property.nodeName == 'skos:inScheme'):
                property_attr = o_property.attributes.items()[0][1]
                concept_schemes.add(property_attr)
    return concept_schemes


def create_inverse_hierarchy(dom):
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
                prop_inverse = inverse_property(prop_name)
                prop_attr = o_property.attributes.items()[0][1]

                if prop_attr not in hierarchy_dict:
                    hierarchy_dict[prop_attr] = {}
                    hierarchy_dict[prop_attr][prop_name] = [o_concept_id]
                elif prop_name not in hierarchy_dict[prop_attr]:
                    hierarchy_dict[prop_attr][prop_name] = [o_concept_id]
                else:
                    hierarchy_dict[prop_attr][prop_name].append(o_concept_id)
    return hierarchy_dict


def inverse_property(property_name):
    if property_name == 'skos:broader':
        return 'skos:narrower'
    elif property_name == 'skos:narrower':
        return 'skos:broader'
    else:
        return 'skos:related'


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


def write_dom_to_file(dom, file):
    # Write a dom to a XML file
    xml_file = open(file, "w")
    xml_file.write(dom.toprettyxml().encode("utf-8"))
    xml_file.close()

# def process_results(dom):
#     write_dom_to_file(dom, transformed_file)
#     save_differences()
#     save_typeless()
#
#
# # Each difference is written to a csv file
# def save_differences():
#     header_list = ['concept 1', 'type of relation', 'concept 2']
#     d_file  = open(issue_file, "wb")
#     writer = csv.writer(d_file)
#     writer.writerow(header_list)
#     for difference in full_list_of_differences:
#         writer.writerow(difference)
#     d_file.close()
#
# # Each typeless concept is written to a csv file
# def save_typeless():
#     b_file  = open(missing_file, "wb")
#     the_writer = csv.writer(b_file)
#     for missing in typeless_concepts:
#         the_writer.writerow([missing])
#     b_file.close()

# The next part runs over all concepts in the root
# for concept in root.childNodes:
#     # Ignore concept schemes just added to dom
#     if concept.nodeName == 'skos:ConceptScheme':
#         continue
#     if concept.nodeType == concept.ELEMENT_NODE:
#         concept_id = concept.attributes.items()[0][1]
#         concept_properties = concept.childNodes
#         # Each property of a concept is stored in a dictionary with the name of the property and its value
#         property_dict = {}
#         for property in concept_properties:
#             if property.nodeType == property.ELEMENT_NODE:
#                 # Properties with text nodes or other nodes and the skos:topConceptOf nodes are excluded from the property dictionary
#                 if property.hasChildNodes():
#                     continue
#                 elif property.nodeName == 'skos:topConceptOf':
#                     continue
#                 else:
#                     label = property.nodeName
#                     attribute_value = property.attributes.items()[0][1]
#                     if label in property_dict:
#                         property_dict[label].append(attribute_value)
#                     else:
#                         property_dict[label] = [attribute_value]
#         # All concepts without the skos:inScheme property are added to the list of schemeless concepts
#         if 'skos:inScheme' not in property_dict:
#             typeless_concepts.append(concept_id)
#         # With the use of a list of relation property labels, the script runs over every relation
#         hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']
#         # The difference between the relations in the property dictionary and in the hierarchical dictionary are found
#         if concept_id in hierarchy_dict:
#             for h_label in hierarchy_labels:
#                 if h_label in property_dict and h_label in hierarchy_dict[concept_id]:
#                     length_property = len(property_dict[h_label])
#                     difference = list(set(property_dict[h_label]) - set(hierarchy_dict[concept_id][h_label]))
#                     if difference != []:
#                         difference_list = [concept_id, h_label, difference]
#                         full_list_of_differences.append(difference_list)
#                         # Each difference will be added to the root
#                         a_remove_list = []
                        # for a_difference in difference:
                            # if a_difference in full_list_of_concepts:
                                # If the difference concept is missing the difference, a new property node will be added to the concept node that missed the relation property.
                                # if a_difference in property_dict[h_label]:
                                #     for another_concept in root.childNodes:
                                #         if another_concept.nodeName == 'skos:ConceptScheme':
                                #             continue
                                #         if another_concept.nodeType == another_concept.ELEMENT_NODE:
                                #             another_concept_id = another_concept.attributes.items()[0][1]
                                #             if another_concept_id == a_difference:
                                #                 if h_label == 'skos:broader':
                                #                     new_node = dom.createElement('skos:narrower')
                                #                     another_concept.appendChild(new_node)
                                #                     new_node.setAttribute('rdf:resource', concept_id)
                                #                     change_file(dom, transformed_file)
                                #                 elif h_label == 'skos:narrower':
                                #                     new_node = dom.createElement('skos:broader')
                                #                     another_concept.appendChild(new_node)
                                #                     new_node.setAttribute('rdf:resource', concept_id)
                                #                     change_file(dom, transformed_file)
                                #                 elif h_label == 'skos:related':
                                #                     new_node = dom.createElement('skos:related')
                                #                     another_concept.appendChild(new_node)
                                #                     new_node.setAttribute('rdf:resource', concept_id)
                                #                     change_file(dom, transformed_file)
# IF the current concept itself is missing the difference relation, a property node will be added to the current concept node
                                # else:
                                #     if h_label in property_dict:
                                #         property_dict[h_label].append(a_difference)
                                #     else:
                                #         property_dict[h_label] = [a_difference]
                                #     new_node = dom.createElement(h_label)
                                #     concept.appendChild(new_node)
                                #     new_node.setAttribute('rdf:resource', a_difference)
                                #     change_file(dom, transformed_file)
# If the difference relation is with a concept not available in the file, the difference will be removed from the property dictionary
                        #     else:
                        #         a_remove_list.append(a_difference)
                        #         for w_property in concept.childNodes:
                        #             if w_property.nodeType == w_property.ELEMENT_NODE:
                        #                 if w_property.nodeName == h_label and w_property.attributes.items()[0][1] == a_difference:
                        #                     concept.removeChild(w_property)
                        #                     change_file(dom, transformed_file)
                        # for z_concept in a_remove_list:
                        #     property_dict[h_label].remove(z_concept)
                        # if h_label in property_dict:
                        #     if len(property_dict[h_label]) < 1:
                        #         del property_dict[h_label]
# Another difference, caused by the absence of a relation label in the property dictionary is handled by adding the missing property relation to the concept
                # elif h_label not in property_dict and h_label in hierarchy_dict[concept_id]:
                #     difference_list = [concept_id, h_label,hierarchy_dict[concept_id][h_label]]
                #     full_list_of_differences.append(difference_list)
                #     for t_dif in hierarchy_dict[concept_id][h_label]:
                #         if h_label in property_dict:
                #             property_dict[h_label].append(t_dif)
                #         else:
                #             property_dict[h_label] = [t_dif]
                #         new_node = dom.createElement(h_label)
                #         concept.appendChild(new_node)
                #         new_node.setAttribute('rdf:resource', t_dif)
                #         change_file(dom, transformed_file)
# Another difference, caused by the absence of a relation label in the hierarchy dictionary is handled by adding the missing property relation to the other concept of the relation
                # elif h_label in property_dict and h_label not in hierarchy_dict[concept_id]:
                #     difference_list = [concept_id, h_label,property_dict[h_label]]
                #     full_list_of_differences.append(difference_list)
                #     q_remove_list = []
                #     for r_dif in property_dict[h_label]:
                #         if r_dif in full_list_of_concepts:
                #             for q_concept in root.childNodes:
                #                 if q_concept.nodeName == 'skos:ConceptScheme':
                #                     continue
                #                 if q_concept.nodeType == q_concept.ELEMENT_NODE:
                #                     q_concept_id = q_concept.attributes.items()[0][1]
                #                     if q_concept_id == r_dif:
                #                         if h_label == 'skos:broader':
                #                             new_node = dom.createElement('skos:narrower')
                #                             q_concept.appendChild(new_node)
                #                             new_node.setAttribute('rdf:resource', concept_id)
                #                             change_file(dom, transformed_file)
                #                         elif h_label == 'skos:narrower':
                #                             new_node = dom.createElement('skos:broader')
                #                             q_concept.appendChild(new_node)
                #                             new_node.setAttribute('rdf:resource', concept_id)
                #                             change_file(dom, transformed_file)
                #                         elif h_label == 'skos:related':
                #                             new_node = dom.createElement('skos:related')
                #                             q_concept.appendChild(new_node)
                #                             new_node.setAttribute('rdf:resource', concept_id)
                #                             change_file(dom, transformed_file)
                #         else:
                #             q_remove_list.append(r_dif)
                #             for w_property in concept.childNodes:
                #                 if w_property.nodeType == w_property.ELEMENT_NODE:
                #                     if w_property.nodeName == h_label and w_property.attributes.items()[0][1] == r_dif:
                #                         concept.removeChild(w_property)
                #                         change_file(dom, transformed_file)
                #     for z_concept in q_remove_list:
                #         property_dict[h_label].remove(z_concept)
                #     if h_label in property_dict:
                #         if len(property_dict[h_label]) < 1:
                #             del property_dict[h_label]
#If a concept does not occur in the hierarchy dictionary, all relations found in the property dictionary are added to the related concepts if the are available in the file
        # else:
        #     for t_label in hierarchy_labels:
        #         if t_label in property_dict:
        #             difference_list = [concept_id, t_label,property_dict[t_label]]
        #             full_list_of_differences.append(difference_list)
        #             remove_list = []
        #             for r_concept in property_dict[t_label]:
        #                 if r_concept in full_list_of_concepts:
        #                     if t_label == 'skos:broader':
        #                         t_label = 'skos:narrower'
        #                     elif t_label == 'skos:narrower':
        #                         t_label = 'skos:broader'
        #                     for w_concept in root.childNodes:
        #                         if w_concept.nodeType == w_concept.ELEMENT_NODE:
        #                             w_concept_id = w_concept.attributes.items()[0][1]
        #                             if w_concept_id == r_concept:
        #                                 new_node = dom.createElement(t_label)
        #                                 w_concept.appendChild(new_node)
        #                                 new_node.setAttribute('rdf:resource', concept_id)
        #                                 change_file(dom, transformed_file)
        #                 else:
        #                     remove_list.append(r_concept)
        #                     for w_property in concept.childNodes:
        #                         if w_property.nodeType == w_property.ELEMENT_NODE:
        #                             if w_property.nodeName == t_label and w_property.attributes.items()[0][1] == r_concept:
        #                                 concept.removeChild(w_property)
        #                                 change_file(dom, transformed_file)
        #             for z_concept in remove_list:
        #                 property_dict[t_label].remove(z_concept)
        #             if t_label in property_dict:
        #                 if len(property_dict[t_label]) < 1:
        #                     del property_dict[t_label]
# The last change is the addition of skos:topConceptOf nodes to concepts without any broader relations. These nodes are created for every scheme of the concept.
        # if 'skos:broader' not in property_dict:
        #     if 'skos:inScheme' in property_dict:
        #         for scheme in property_dict['skos:inScheme']:
        #             new_node = dom.createElement('skos:topConceptOf')
        #             concept.appendChild(new_node)
        #             new_node.setAttribute('rdf:resource', scheme)
#Each ConceptScheme node gets a skos:hasTopConcept node with the concept that got a 'skos:topConceptOf node with the same attribute value
                    # for a_concept in root.childNodes:
                    #     if a_concept.nodeType == a_concept.ELEMENT_NODE:
                    #         if a_concept.nodeName == 'skos:ConceptScheme':
                    #             attr_value = a_concept.attributes.items()[0][1]
                    #             if attr_value == scheme:
                    #                 extra_node = dom.createElement('skos:hasTopConcept')
                    #                 a_concept.appendChild(extra_node)
                    #                 extra_node.setAttribute('rdf:resource', concept_id)
                    #                 change_file(dom, transformed_file)
#The typeless concepts without broader relations are related with the UNKNOWN ConceptScheme nodes
            # else:
            #     new_node = dom.createElement('skos:topConceptOf')
            #     concept.appendChild(new_node)
            #     new_node.setAttribute('rdf:resource', 'Unknown')
            #     for a_concept in root.childNodes:
            #         if a_concept.nodeType == a_concept.ELEMENT_NODE:
            #             if a_concept.nodeName == 'skos:ConceptScheme':
            #                 attr_value = a_concept.attributes.items()[0][1]
            #                 if attr_value == 'Unknown':
            #                     extra_node = dom.createElement('skos:hasTopConcept')
            #                     a_concept.appendChild(extra_node)
            #                     extra_node.setAttribute('rdf:resource', concept_id)
            #                     change_file(dom, transformed_file)

if __name__ == "__main__":
    main()
