#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze thesauri

Script with functions to analyze a thesaurus.
"""

__author__ = "Quinten van Langen"
__version__ = "1.0.0"
__license__ = "cc0-1.0"


import pickle
import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime
import random
from sets import Set
import re
from anytree import Node

def time(start):
    return datetime.now() - start

def find_matches(dict1): # Create a list and dictionary of stored matches
    matches_dict = {}
    AAT_match_list = []
    Dutch_AAT_match_list = []
    misplaced_AAT_list = []

    for concept in dict1:
        matches = dict1[concept]['matches']
        for match in matches:
            if 'aat' in match:
                if 'vocab.getty.edu' in match:
                    match = re.findall(r'\b\d+\b', match)[-1]
                    matches_dict[match] = concept
                    AAT_match_list.append(match)
                elif 'browser.aat-ned' in match:
                    matches_dict[match] = concept
                    Dutch_AAT_match_list.append(match)
                else:
                    misplaced_AAT_list.append(match)
    AAT_match_list = list(set(AAT_match_list))
    print('{} Created lists and dictionary of AAT matches'
    .format(time(start)))
    return matches_dict, AAT_match_list, Dutch_AAT_match_list, misplaced_AAT_list
    
def match_in_AAT(AAT_dict, AAT_match_list): # Check if a match is present in the AAT dictionary
    matches_in_aat_dict = {}
    matches_in_aat_list = []
    for concept in AAT_dict:
        the_id = str(AAT_dict[concept]['id'])
        if the_id in AAT_match_list:
            matches_in_aat_dict[concept] = the_id
            matches_in_aat_list.append(the_id)

    matches_in_aat_list = list(set(matches_in_aat_list))
    print('{} Searched for the matches in AAT'
    .format(time(start)))
    return matches_in_aat_list, matches_in_aat_dict

def matches_not_in_parse(match_dict, match_list1, match_list2, RT_dict): # determine the amount of matches that are not parsed from the AAT
    difference_list = list(set(match_list1) - set(match_list2))
    missing_aat_list = []
    for difference in difference_list:
        missing_aat_list.append(RT_dict[match_dict[difference]])
    return missing_aat_list

def own_overlap(thesaurus_dict): #Look at the overlap in labels within a thesaurus
    copy_dict = dict(thesaurus_dict)
    the_own_overlap_dict = {}
    label_list = []

    for concept1 in thesaurus_dict:
        labels_concept1 = thesaurus_dict[concept1]['prefLabel'] + thesaurus_dict[concept1]['altLabel']
        concept1 = re.findall(r'\b\d+\b', concept1)[-1]
        for a_label in labels_concept1:
            for concept2 in copy_dict:
                labels_concept2 = copy_dict[concept2]['prefLabel'] + copy_dict[concept2]['altLabel']
                concept2 = re.findall(r'\b\d+\b', concept2)[-1]         
                if a_label in labels_concept2:
                    combination_list = [concept2, a_label]
                    combination_list2 = [concept1, a_label]
                    if combination_list == combination_list2:
                        continue
                    if a_label not in label_list:
                        if concept2 in the_own_overlap_dict and combination_list2 in the_own_overlap_dict[concept2]:
                            continue
                        else:
                            if concept1 not in the_own_overlap_dict:
                                the_own_overlap_dict[concept1] = [combination_list]
                            elif combination_list not in the_own_overlap_dict[concept1]:
                                the_own_overlap_dict[concept1].append(combination_list)
            label_list.append(a_label)
    the_own_overlap_list = restructure_dict_to_list(the_own_overlap_dict)
    return the_own_overlap_dict

def store_dict(dict, picklefile): # Store a Python dictionary in a pickle file
    output = open(picklefile, wb)
    pickle.dump(dict, output)
    output.close()

def restructure_dict_to_list(dict): # Restructures the own overlap dictionary to a list
    return_list = []
    for overlap in dict:
        for a_list in dict[overlap]:
            new_list = [overlap] + a_list
            return_list.append(new_list)
    return return_list

def find_overlap(full_dict1, full_dict2): # Search for all overlapping concepts based on the labels
    overlap_dict = {}
    for concept1 in full_dict1:
        concept1_labels = full_dict1[concept1]['prefLabel'] + full_dict1[concept1]['altLabel']
        for a_label in concept1_labels:
            for concept2 in full_dict2:
                concept2_labels = full_dict2[concept2]['prefLabel'] + full_dict2[concept2]['altLabel']
                if a_label in AAT_labels:
                    concept1_matches = full_dict1[concept1]['matches']
                    if concept1 in overlap_dict:
                        overlap_dict[concept1].append(a_label)
                    else:
                        overlap_dict[concept1] = [concept2, rt_matches, a_label]

    store_dict(overlap_dict, 'overlap_dict2.pkl')
    print('{} Finished looking at ovelap and stored the overlapping concepts in a dictionary'
    .format(time(start)))
    return overlap_dict

def matched_overlap(overlap_dict, match_dict): #Look at the amount of overlapping concepts have a match stored as url
    count = 0
    stored_match_types = {}
    overlap_list = []
    for overlap in overlap_dict:
        list_of_labels = create_list_of_labels(overlap_dict[overlap])
        the_id = re.findall(r'\b\d+\b', overlap)[-1]
        overlap_list.append(the_id + list_of_labels)
        if the_id in match_dict:
            concept1 = overlap_dict[overlap][0]
            concept_types = full_RT[RT_concept]['schemes']
            for a_type in concept_types:
                if a_type not in stored_match_types:
                    stored_match_types[a_type] = 1
                else:
                    stored_match_types[a_type] += 1
            count += 1
    print('{} {} of the {} overlapping concepts are already matched'
    .format(time(start), count, len(overlap_dict)))
    matched_overlap_count = count
    return matched_overlap_count, stored_match_types, overlap_list

def create_list_of_labels(dict_list): #creates a list of labels from the list made for the overlap dictionary
    return_list = []
    label_list = []
    for item in dict_list:
        if dict_list.index(item) > 1:
            label_list.append(item)
        else:
            return_list.append(item)
    return_list.append(label_list)
    return return_list

def find_type_of_overlap(overlap_dict, full_dict): # Look at the types and their amounts of the overlap concepts
    overlap_types = {}
    for overlap in overlap_dict:
        the_concept = overlap_dict[overlap][0]
        the_types = full_dict[the_concept]['schemes']
        for a_type in the_types:
            if a_type not in overlap_types:
                overlap_types[a_type] = 1
            else:
                overlap_types[a_type] += 1
    return overlap_types

def write_to_xlsxfile(values, filename, sheet_name, headers):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    if type(values) == dict:
        if headers == []:
            the_dataframe = pd.Dataframe.from_dict(values, orient='index')
        else:
            the_dataframe = pd.Dataframe.from_dict(values, orient='index', columns=headers)
    elif type(values) == list:
        if headers == []:
            the_dataframe = pd.Dataframe(values)
        else:
            the_dataframe = pd.Dataframe(values, columns=headers)
    else:
        return None
    the_dataframe.t0_excel(writer, sheet_name= sheet_name)
    writer.close()

def load_dictionaries(): # Load pickle dictionaries

    start = datetime.now()
    os.chdir('out')
    # Load the Rijksmuseum thesaurus, AAT and overlap dictionaries
    full_RT = pickle.load( open( "full2_dictionary.pkl", "rb" ) )
    print('{} Loaded the Rijksmuseum dictionary'
    .format(time(start)))

    full_AAT = pickle.load(open('AAT/AAT_full_dictionary.pkl', 'rb'))
    print('{} Loaded the AAT dictionary'
    .format(time(start)))

    overlap_dict = pickle.load(open('overlap_dict.pkl', 'rb'))
    print('{} Loaded the overlap dictionary'
    .format(time(start)))

    full_own = pickle.load( open( "own_overlap_dict.pkl", "rb" ) )
    print('{} Loaded the own Rijksmuseum overlap dictionary with a length of {}'
    .format(time(start), len(full_own)))

    full_own_AAT = pickle.load( open( "shorten_own_overlap_dict_AAT.pkl", "rb" ) )
    print('{} Loaded the own overlap AAT dictionary with a length of {}'
    .format(time(start), len(full_own_AAT)))

def list_concepts(dom):
    # Create a list with the id's of the SKOS concepts
    concept_identifiers = []
    root = dom.childNodes.item(0)

    for node in root.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == 'skos:Concept'):
            concept_id = node.attributes.items()[0][1]
            concept_identifiers.append(concept_id)
    return concept_identifiers


def referenced_concept_schemes(dom):
    # List all concept schemes referenced in the thesaurus
    concept_schemes = []
    root = dom.childNodes.item(0)

    for node in root.childNodes:
        for property in node.childNodes:
            if (property.nodeType == property.ELEMENT_NODE
            and property.nodeName == 'skos:inScheme'):
                concept_scheme = property.attributes.items()[0][1]
                if concept_scheme not in concept_schemes:
                    concept_schemes.append(concept_scheme)
    return concept_schemes


def list_schemeless_concepts(dom):
    # List all concepts without that do not reference a concept scheme
    schemeless_concepts = []
    root = dom.childNodes.item(0)

    for node in root.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == 'skos:Concept'):
            concept_id = node.attributes.items()[0][1]
            in_scheme = False

            for property in node.childNodes:
                if property.nodeName == 'skos:inScheme':
                    in_scheme = True
            if not in_scheme:
                schemeless_concepts.append(concept_id)
    return schemeless_concepts


def create_inverse_hierarchy(dom):
    # The inverse of every hierarchical skos relation is added to a dictionary:
    # {'http://concept.net/2': {'skos:broader': ['http://concept.net/1']}}
    hierarchy_dict = {}
    hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']
    root = dom.childNodes.item(0)

    for node in root.childNodes:
        for property in node.childNodes:
            if (property.nodeType == property.ELEMENT_NODE
            and (property.nodeName in hierarchy_labels)):
                concept_id = node.attributes.items()[0][1]
                prop_name = property.nodeName
                prop_inv = inverse_property(prop_name)
                object_id = property.attributes.items()[0][1]

                if object_id not in hierarchy_dict:
                    hierarchy_dict[object_id] = {}
                    hierarchy_dict[object_id][prop_inv] = [concept_id]
                elif prop_inv not in hierarchy_dict[object_id]:
                    hierarchy_dict[object_id][prop_inv] = [concept_id]
                else:
                    hierarchy_dict[object_id][prop_inv].append(concept_id)
    return hierarchy_dict



def inverse_property(property_name):
    if property_name == 'skos:broader':
        return 'skos:narrower'
    elif property_name == 'skos:narrower':
        return 'skos:broader'
    else:
        return 'skos:related'


def missing_outward_references(dom):
    inverse_hierarchy = create_inverse_hierarchy(dom)
    missing_references = []

    # Iterate through all concepts in inverse_hierarchy to check whether
    # all deduced references are present for the concept in question
    for concept_id in inverse_hierarchy:
        concept = get_concept(dom, concept_id)
        if concept is not None:
            properties = hierarchical_properties_dict(concept, 'no')
            i_properties = inverse_hierarchy[concept_id]
            missing = outward_difference(concept_id, properties, i_properties)
            if missing != []:
                missing_references.append(missing)
    return missing_references


def outward_difference(concept_id, props, i_props):
    missing_references = []

    for h_label in i_props:
        if h_label in i_props and h_label in props:
            diff = list(set(i_props[h_label]) - set(props[h_label]))
        else:
            diff = i_props[h_label]
        if diff != []:
            missing = [concept_id, h_label, diff]
            missing_references.append(missing)
    return missing_references
    

def get_concept(dom, concept_id):
    root = dom.childNodes.item(0)

    for node in root.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == 'skos:Concept'):
            if concept_id == node.attributes.items()[0][1]:
                return node
    return None

def get_concept_scheme(dom, scheme):
    root = dom.childNodes.item(0)
    for node in root.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == 'skos:ConceptScheme'):
            if scheme == node.attributes.items()[0][1]:
                return node
    return None


def get_relation_property(concept, property, attribute):
    for node in concept.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == property 
        and node.attributes.items()[0][1] == attribute):
            return node
    return None


def undefined_concept_references(dom):
    missing_references = []
    concepts = list_concepts(dom)
    root = dom.childNodes.item(0)
    hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']

    # Iterate through all concepts to check if they include references
    # to concepts that do not exist
    for node in root.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == 'skos:Concept'):
            concept_id = node.attributes.items()[0][1]

            for property in node.childNodes:
                if (property.nodeType == property.ELEMENT_NODE
                and property.nodeName in hierarchy_labels):
                    object_id = property.attributes.items()[0][1]
                    h_label = property.nodeName
                    if object_id not in concepts:
                        missing = [concept_id, h_label, object_id]
                        missing_references.append(missing)
    return missing_references


def hierarchical_properties_dict(node, extra):
    # Each hierarchical property is stored in a dictionary with the name of the
    # property and its value.
    hierarchical_properties = {}
    hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']

    for property in node.childNodes:
        if (property.nodeType == property.ELEMENT_NODE
        and property.nodeName in hierarchy_labels):
            prop_name = property.nodeName
            if extra == 'yes':
                object_id = re.findall(r'\b\d+\b', property.attributes.items()[0][1])[-1]
            else:
                object_id = property.attributes.items()[0][1]
            if prop_name in hierarchical_properties:
                hierarchical_properties[prop_name].append(object_id)
            else:
                hierarchical_properties[prop_name] = [object_id]
    return hierarchical_properties

def label_properties_dict(node):
    # Each label is stored in a dictionary with the label itself and it's language
    label_properties = {}
    label_labels = ['skos:prefLabel', 'skos:altLabel']
    label_properties['prefLabel'] = []
    label_properties['altLabel'] = []
    for property in node.childNodes:
        if (property.nodeType == property.ELEMENT_NODE
        and property.nodeName in label_labels):
            property_dict = {}
            prop_name = property.nodeName[5:]
            language = str(property.attributes.items()[0][1])
            label = str(property.childNodes[0].data.encode('utf-8'))
            property_dict['language'] = language
            property_dict['label'] = label
            label_properties[prop_name].append(property_dict)
    return label_properties

def extra_properties_dict(node):
    # Some extra properties for a concept are stored in a dictionary
    extra_properties_dict = {}
    extra_labels = ['skos:scopeNote', 'skos:exactMatch', 'skos:topConceptOf']
    create_labels = ['notes', 'matches']
    for label in create_labels:
        extra_properties_dict[label] = []
    topConcept_count = 0
    for property in node.childNodes:
        if (property.nodeType == property.ELEMENT_NODE
        and property.nodeName in extra_labels):
            prop_name = property.nodeName[5:]
            if prop_name == 'scopeNote':
                the_note = str(property.childNodes[0].data.encode('utf-8'))
                extra_properties_dict['notes'].append(the_note)
            elif prop_name == 'topConceptOf':
                topConcept_count += 1
            elif prop_name == 'exactMatch':
                match = property.attributes.items()[0][1]
                extra_properties_dict['matches'].append(match)
    extra_properties_dict['#Top concepts'] = topConcept_count
    return extra_properties_dict

def restructure_missing_references(a_list):
    # Restructures the list of missing references
    return_list = []
    for i in a_list:
        for j in i:
            another_list = j[-1]
            j.pop()
            for the in another_list:
                copy_j = list(j)
                copy_j.append(str(the))
                return_list.append(copy_j)
    return return_list

def find_top_concepts(dom):
    # Create a list of concepts without broader concepts
    root = dom.childNodes.item(0)
    list_of_top_concepts = []
    for node in root.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == 'skos:Concept'):
            hierarchical_properties = hierarchical_properties_dict(node, 'no')
            concept_id = node.attributes.items()[0][1]
            if 'skos:broader' not in hierarchical_properties:
                list_of_top_concepts.append(concept_id)
    return list_of_top_concepts

def find_all_schemes(dom, extra):
    # Create a dictionary which stores all schemes of a concept
    schemes_dict = {}
    root = dom.childNodes.item(0)
    for node in root.childNodes:
        if (node.nodeType == node.ELEMENT_NODE
        and node.nodeName == 'skos:Concept'):
            if extra == 'yes':
                concept_id = re.findall(r'\b\d+\b', node.attributes.items()[0][1])[-1]
            else:
                concept_id = node.attributes.items()[0][1]
            schemes_dict[concept_id] = []
            for property in node.childNodes:
                if property.nodeName == 'skos:inScheme':
                    if extra == 'yes':
                        scheme_label = property.attributes.items()[0][1][42:]
                    else:
                        scheme_label = property.attributes.items()[0][1]
                    schemes_dict[concept_id].append(scheme_label)
    return schemes_dict

def all_properties(dom, extra):
    # Create a list of all relevant properties for each concept
    all_properties_dict = {}
    schemes_dict = find_all_schemes(dom, 'yes')
    root = dom.childNodes.item(0)
    for concept in root.childNodes:
        if (concept.nodeType == concept.ELEMENT_NODE
        and concept.nodeName == 'skos:Concept'):
            concept_id = re.findall(r'\b\d+\b', concept.attributes.items()[0][1])[-1]
            all_properties_dict[concept_id] = {}
            all_properties_dict[concept_id]["id"] = concept_id
            all_properties_dict[concept_id].update(hierarchical_properties_dict(concept, 'yes'))
            hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']
            for label in hierarchy_labels:
                if label not in all_properties_dict[concept_id]:
                    all_properties_dict[concept_id][label] = []
            all_properties_dict[concept_id].update(label_properties_dict(concept))
            if extra == 'yes':
                all_properties_dict[concept_id]['schemes'] = schemes_dict[concept_id]
                all_properties_dict[concept_id].update(extra_properties_dict(concept))
    all_properites_dict = determine_depth(all_properties_dict)

    all_properties_list = []
    for a_concept in all_properties_dict:
        all_properties_list.append(all_properties_dict[a_concept])
    return all_properties_list



def determine_depth(concept_dict):
    # Determining the depth of each concept in the hierarchical tree
    list_of_tuples = []
    node_dict = {}
    for concept in concept_dict:
        concept_id = concept_dict[concept]['id']
        node_dict[concept_id] = Node(str(concept_id))
        broader = concept_dict[concept]['skos:broader']
        if broader == []:
            continue
        for b in broader:
            new_tuple = (concept_id, b)
            if new_tuple not in list_of_tuples:
                list_of_tuples.append(new_tuple)
    for j in list_of_tuples:
        child = j[0]
        parent = j[1]
        if child == parent:
            continue
        if child in concept_dict and parent in concept_dict:
            node_dict[child].parent = node_dict[parent]
    for concept in concept_dict:
        depth = int(len(node_dict[concept_dict[concept]['id']].path) - 1)
        concept_dict[concept]['Depth'] = depth
    return concept_dict

def reference_analyse(list):
    # Perform quantitative analysis of the reference properties
    references_dict = {}
    total_broader = {}
    total_narrower = {}
    total_related = {}
    for concept in list:
        broader = concept['skos:broader']
        narrower = concept['skos:narrower']
        related = concept['skos:related']
        number_broader = len(broader)
        number_narrower = len(narrower)
        number_related = len(related)
        references_dict[concept['id']] = [number_broader, number_narrower, number_related]
        total = number_broader + number_narrower + number_related
        if number_broader in total_broader:
            total_broader[number_broader] += 1
        else:
            total_broader[number_broader] = 1
        if number_narrower in total_narrower:
            total_narrower[number_narrower] += 1
        else:
            total_narrower[number_narrower] = 1
        if number_related in total_related:
            total_related[number_related] += 1
        else:
            total_related[number_related] = 1
    return_list = [total_broader, total_narrower, total_related]
    reference_dict = create_reference_dict(references_dict)
    return reference_dict, return_list

def create_reference_dict(dict):
    # Create a type of dictionary about all references of a concept
    reference_dict = {}
    for concept in dict:
        references = dict[concept]
        string_references = ""
        for i in references:
            string_references += str(i)
            string_references += '-'
        string_references = ''.join(string_references.split())[:-1].upper()
        if string_references in reference_dict:
            reference_dict[string_references] += 1
        else:
            reference_dict[string_references] = 1
    return reference_dict

def label_analyse(list):
    # Perform a quantitative analysis on the labels of a concept
    concept_label_dict = {}
    count_label_dict = {}
    language_label_dict = {}
    count_label_dict ['pref'] = {}
    count_label_dict ['alt'] = {}
    language_label_dict ['pref'] = {}
    language_label_dict ['alt'] = {}
    for concept in list:
        concept_id = concept['id']
        label_dict = {}
        pref = concept['prefLabel']
        alt = concept['altLabel']
        label_dict['pref'] = pref
        label_dict['alt'] = alt
        if len(pref) in count_label_dict ['pref']:
            count_label_dict ['pref'][len(pref)] += 1
        else:
            count_label_dict ['pref'][len(pref)] = 1
        if len(alt) in count_label_dict ['alt']:
            count_label_dict ['alt'][len(alt)] += 1
        else:
            count_label_dict ['alt'][len(alt)] = 1
        label_dict['#pref'] = len(pref)
        label_dict['#alt'] = len(alt)
        pref_language_list = []
        for i in pref:
            language = i['language']
            pref_language_list.append(language)
            language_label_dict ['pref'][language] = language_label_dict ['pref'].get(language, 0) + 1
        label_dict['Pref languages'] = pref_language_list
        alt_language_list = []
        for i in alt:
            language = i['language']
            alt_language_list.append(language)
            language_label_dict ['alt'][language] = language_label_dict ['alt'].get(language, 0) + 1
        label_dict['Alt languages'] = alt_language_list
        concept_label_dict[concept['id']] = label_dict
    return concept_label_dict, language_label_dict, count_label_dict

def is_number(s):
    # Check if a string is a number
    try:
        float(s)
        return True
    except ValueError:
        return False    

def matches_analyse(list):
    # Perform a quantitative 
    key_list = ['none', 'AAT', 'TGN', 'MIMO', 'Wiki', 'Numbers', 'Geonames', 'other']
    number_matches_dict = {}
    for key in key_list:
        number_matches_dict[key] = 0
    for concept in list:
        if len(concept['matches']) == 0:
            number_matches_dict['none'] += 1
        else:
            for match in concept['matches']:
                if 'aat' in match:
                    number_matches_dict['AAT'] += 1
                elif 'tgn' in match or 'TGN' in match:
                    number_matches_dict['TGN'] += 1
                elif 'mimo' in match:
                    number_matches_dict['MIMO'] += 1
                elif 'wiki' in match:
                    number_matches_dict['Wiki'] += 1  
                elif is_number(match):
                    number_matches_dict['Numbers'] += 1  
                elif 'geonames' in match:
                    number_matches_dict['Geonames'] += 1
                else:
                    number_matches_dict['other'] += 1
    return number_matches_dict

def type_analyse(list):
    scheme_dict = {}
    for concept in list:
        schemes = concept['schemes']
        for scheme in schemes:
            scheme_dict[scheme] = scheme_dict.get(scheme, 0) + 1
    return scheme_dict