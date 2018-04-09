'''
Created on 13 mrt. 2018

@author: Gebruiker
'''
# Import all necessary packages
import os 
import csv
from xml.dom.minidom import parse
from shutil import copyfile
from datetime import datetime
# Save the start time, to calculate the full run time of the script
startTime = datetime.now()

# The name specifications of the used and created files
orginial_file = 'full_skos.rdf'
transformed_file = 'Full_transformed.rdf'
issue_file = 'full_differences.csv'
missing_file = 'full_missing.csv'
os.chdir('../thesaurus_export') # The location to store and access the files

# Definition that opens a XML file and updates the changes made
def change_file(root, file):
    xml_file = open(file, "w")
    xml_file.write(root.toprettyxml().encode("utf-8"))
    xml_file.close()

# Start a run over the original file to create list and dictionaries
dom = parse(orginial_file)
o_rdf = dom.childNodes.item(0)
scheme_values = ['Unknown']
hierarchy_dict = {}
full_list_of_concepts = []
# The firt list created is a list with the id's of the concepts
for o_concept in o_rdf.childNodes:
    if o_concept.nodeType == o_concept.ELEMENT_NODE:
        o_concept_id = o_concept.attributes.items()[0][1]
        full_list_of_concepts.append(o_concept_id)
# Secondly a run over all properties of a concept is done
        for o_property in o_concept.childNodes:
# A list of schemes is created
            if o_property.nodeType == o_property.ELEMENT_NODE:
                if o_property.nodeName == 'skos:inScheme':
                    property_attr = o_property.attributes.items()[0][1]
                    if property_attr not in scheme_values:
                        scheme_values.append(property_attr)
# For each type of relation, the inverse relation will be added to a dictionary
                if o_property.nodeName == 'skos:broader' or o_property.nodeName == 'skos:narrower' or o_property.nodeName == 'skos:related':
                    prop_name = o_property.nodeName
                    if prop_name == 'skos:broader':
                        prop_name = 'skos:narrower'
                    elif prop_name == 'skos:narrower':
                        prop_name = 'skos:broader'
                    else:
                        prop_name = 'skos:related'
                    prop_attr = o_property.attributes.items()[0][1]
                    if prop_attr not in hierarchy_dict:
                        hierarchy_dict[prop_attr] = {}
                        hierarchy_dict[prop_attr][prop_name] = [o_concept_id]
                    elif prop_name not in hierarchy_dict[prop_attr]:
                        hierarchy_dict[prop_attr][prop_name] = [o_concept_id]
                    else:
                        hierarchy_dict[prop_attr][prop_name].append(o_concept_id)

# The transformed file is an exact copy of the original file
copyfile(orginial_file, transformed_file)

# List of differences and typeless concepts are created
full_list_of_differnces = []
typeless_concepts = []
# The root of the RDF file is found and selected
n_dom = parse(transformed_file)
childs = n_dom.childNodes
root = childs.item(0)
# The first change is the addition of skos:ConceptScheme nodes to the root for each scheme value
for scheme in scheme_values:
    if scheme == 'Unknown':
        scheme_node = n_dom.createElement('skos:ConceptScheme')
        root.appendChild(scheme_node)
        scheme_node.setAttribute('rdf:about', scheme)
        concept_node = n_dom.createElement('dct:title')
        scheme_node.appendChild(concept_node)
        concept_node.setAttribute('xml:lang', 'nl')
        text_node = n_dom.createTextNode(scheme)
        concept_node.appendChild(text_node)
        change_file(n_dom, transformed_file)
    else:
        scheme_node = n_dom.createElement('skos:ConceptScheme')
        root.appendChild(scheme_node)
        scheme_node.setAttribute('rdf:about', scheme)
        concept_node = n_dom.createElement('dct:title')
        scheme_node.appendChild(concept_node)
        concept_node.setAttribute('xml:lang', 'nl')
        text_node = n_dom.createTextNode(scheme[42:])
        concept_node.appendChild(text_node)
        change_file(n_dom, transformed_file)

# The next part runs over all concepts in the root
for concept in root.childNodes:
    if concept.nodeName == 'skos:ConceptScheme':
        continue
    if concept.nodeType == concept.ELEMENT_NODE:
        concept_id = concept.attributes.items()[0][1]
        concept_properties = concept.childNodes
# Each property of a concept is stored in a dictionary with the name of the property and its value
        property_dict = {}
        for property in concept_properties:
            if property.nodeType == property.ELEMENT_NODE:
#Properties with text nodes or other nodes and the skos:topConceptOf nodes are excluded from the property dictionary
                if property.hasChildNodes():
                    continue 
                elif property.nodeName == 'skos:topConceptOf':
                    continue
                else:
                    label = property.nodeName
                    attribute_value = property.attributes.items()[0][1]
                    if label in property_dict:
                        property_dict[label].append(attribute_value)
                    else:                        
                        property_dict[label] = [attribute_value]
# All concepts without the skos:inScheme property are added to the list of typeless concepts
        if 'skos:inScheme' not in property_dict:
            typeless_concepts.append(concept_id)
# With the use of a list of relation property labels, the script runs over every relations
        hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']
#The difference between the relations in the property dictionary and in the hierarchical dictionary are found
        if concept_id in hierarchy_dict:
            for h_label in hierarchy_labels:
                if h_label in property_dict and h_label in hierarchy_dict[concept_id]:
                    length_property = len(property_dict[h_label])
                    difference = list(set(property_dict[h_label]) - set(hierarchy_dict[concept_id][h_label]))
                    if difference != []:
                        difference_list = [concept_id, h_label, difference]
                        full_list_of_differnces.append(difference_list)
# Each difference will be added to the root
                        a_remove_list = []
                        for a_difference in difference:
                            if a_difference in full_list_of_concepts:
# If the difference concept is missing the difference, a new property node will be added to the concept node that missed the relation property. 
                                if a_difference in property_dict[h_label]:
                                    for another_concept in root.childNodes:
                                        if another_concept.nodeName == 'skos:ConceptScheme':
                                            continue
                                        if another_concept.nodeType == another_concept.ELEMENT_NODE:
                                            another_concept_id = another_concept.attributes.items()[0][1]
                                            if another_concept_id == a_difference:
                                                if h_label == 'skos:broader':
                                                    new_node = n_dom.createElement('skos:narrower')
                                                    another_concept.appendChild(new_node)
                                                    new_node.setAttribute('rdf:resource', concept_id)
                                                    change_file(n_dom, transformed_file)
                                                elif h_label == 'skos:narrower':
                                                    new_node = n_dom.createElement('skos:broader')
                                                    another_concept.appendChild(new_node)
                                                    new_node.setAttribute('rdf:resource', concept_id)
                                                    change_file(n_dom, transformed_file)
                                                elif h_label == 'skos:related':
                                                    new_node = n_dom.createElement('skos:related')
                                                    another_concept.appendChild(new_node)
                                                    new_node.setAttribute('rdf:resource', concept_id)
                                                    change_file(n_dom, transformed_file)
# IF the current concept itself is missing the difference relation, a property node will be added to the current concept node
                                else:
                                    if h_label in property_dict:
                                        property_dict[h_label].append(a_difference)
                                    else:
                                        property_dict[h_label] = [a_difference]
                                    new_node = n_dom.createElement(h_label)
                                    concept.appendChild(new_node)
                                    new_node.setAttribute('rdf:resource', a_difference)
                                    change_file(n_dom, transformed_file)
# If the difference relation is with a concept not available in the file, the difference will be removed from the property dictionary
                            else:
                                a_remove_list.append(a_difference)
                                for w_property in concept.childNodes:
                                    if w_property.nodeType == w_property.ELEMENT_NODE:
                                        if w_property.nodeName == h_label and w_property.attributes.items()[0][1] == a_difference:
                                            concept.removeChild(w_property)
                                            change_file(n_dom, transformed_file)
                        for z_concept in a_remove_list:
                            property_dict[h_label].remove(z_concept)
                        if h_label in property_dict:
                            if len(property_dict[h_label]) < 1:
                                del property_dict[h_label]
# Another difference, caused by the absence of a relation label in the property dictionary is handled by adding the missing property relation to the concept
                elif h_label not in property_dict and h_label in hierarchy_dict[concept_id]:
                    difference_list = [concept_id, h_label,hierarchy_dict[concept_id][h_label]]
                    full_list_of_differnces.append(difference_list)
                    for t_dif in hierarchy_dict[concept_id][h_label]:
                        if h_label in property_dict:
                            property_dict[h_label].append(t_dif)
                        else:
                            property_dict[h_label] = [t_dif]
                        new_node = n_dom.createElement(h_label)
                        concept.appendChild(new_node)
                        new_node.setAttribute('rdf:resource', t_dif)
                        change_file(n_dom, transformed_file)
# Another difference, caused by the absence of a relation label in the hierarchy dictionary is handled by adding the missing property relation to the other concept of the relation
                elif h_label in property_dict and h_label not in hierarchy_dict[concept_id]:
                    difference_list = [concept_id, h_label,property_dict[h_label]]
                    full_list_of_differnces.append(difference_list)
                    q_remove_list = []
                    for r_dif in property_dict[h_label]:
                        if r_dif in full_list_of_concepts:
                            for q_concept in root.childNodes:
                                if q_concept.nodeName == 'skos:ConceptScheme':
                                    continue
                                if q_concept.nodeType == q_concept.ELEMENT_NODE:
                                    q_concept_id = q_concept.attributes.items()[0][1]
                                    if q_concept_id == r_dif:
                                        if h_label == 'skos:broader':
                                            new_node = n_dom.createElement('skos:narrower')
                                            q_concept.appendChild(new_node)
                                            new_node.setAttribute('rdf:resource', concept_id)
                                            change_file(n_dom, transformed_file)
                                        elif h_label == 'skos:narrower':
                                            new_node = n_dom.createElement('skos:broader')
                                            q_concept.appendChild(new_node)
                                            new_node.setAttribute('rdf:resource', concept_id)
                                            change_file(n_dom, transformed_file)
                                        elif h_label == 'skos:related':
                                            new_node = n_dom.createElement('skos:related')
                                            q_concept.appendChild(new_node)
                                            new_node.setAttribute('rdf:resource', concept_id)
                                            change_file(n_dom, transformed_file)
                        else:
                            q_remove_list.append(r_dif)
                            for w_property in concept.childNodes:
                                if w_property.nodeType == w_property.ELEMENT_NODE:
                                    if w_property.nodeName == h_label and w_property.attributes.items()[0][1] == r_dif:
                                        concept.removeChild(w_property)
                                        change_file(n_dom, transformed_file)
                    for z_concept in q_remove_list:
                        property_dict[h_label].remove(z_concept)
                    if h_label in property_dict:
                        if len(property_dict[h_label]) < 1:
                            del property_dict[h_label]
#If a concept does not occur in the hierarchy dictionary, all relations found in the property dictionary are added to the related concepts if the are available in the file
        else:
            for t_label in hierarchy_labels:
                if t_label in property_dict:
                    difference_list = [concept_id, t_label,property_dict[t_label]]
                    full_list_of_differnces.append(difference_list)
                    remove_list = []
                    for r_concept in property_dict[t_label]:
                        if r_concept in full_list_of_concepts:
                            if t_label == 'skos:broader':
                                t_label = 'skos:narrower'
                            elif t_label == 'skos:narrower':
                                t_label = 'skos:broader'
                            for w_concept in root.childNodes:
                                if w_concept.nodeType == w_concept.ELEMENT_NODE:
                                    w_concept_id = w_concept.attributes.items()[0][1]
                                    if w_concept_id == r_concept:
                                        new_node = n_dom.createElement(t_label)
                                        w_concept.appendChild(new_node)
                                        new_node.setAttribute('rdf:resource', concept_id)
                                        change_file(n_dom, transformed_file)
                        else:
                            remove_list.append(r_concept)
                            for w_property in concept.childNodes:
                                if w_property.nodeType == w_property.ELEMENT_NODE:
                                    if w_property.nodeName == t_label and w_property.attributes.items()[0][1] == r_concept:
                                        concept.removeChild(w_property)
                                        change_file(n_dom, transformed_file)
                    for z_concept in remove_list:
                        property_dict[t_label].remove(z_concept)
                    if t_label in property_dict:
                        if len(property_dict[t_label]) < 1:
                            del property_dict[t_label]
# The last change is the addition of skos:topConceptOf nodes to concepts without any broader relations. These nodes are created for every scheme of the concept.
        if 'skos:broader' not in property_dict:
            if 'skos:inScheme' in property_dict:
                for scheme in property_dict['skos:inScheme']:
                    new_node = n_dom.createElement('skos:topConceptOf')
                    concept.appendChild(new_node)
                    new_node.setAttribute('rdf:resource', scheme)
#Each ConceptScheme node gets a skos:hasTopConcept node with the concept that got a 'skos:topConceptOf node with the same attribute value
                    for a_concept in root.childNodes:
                        if a_concept.nodeType == a_concept.ELEMENT_NODE:
                            if a_concept.nodeName == 'skos:ConceptScheme':
                                attr_value = a_concept.attributes.items()[0][1]
                                if attr_value == scheme:
                                    extra_node = n_dom.createElement('skos:hasTopConcept')
                                    a_concept.appendChild(extra_node)
                                    extra_node.setAttribute('rdf:resource', concept_id)
                                    change_file(n_dom, transformed_file)
#The typeless concepts without broader relations are related with the UNKNOWN ConceptScheme nodes
            else:
                new_node = n_dom.createElement('skos:topConceptOf')
                concept.appendChild(new_node)
                new_node.setAttribute('rdf:resource', 'Unknown')
                for a_concept in root.childNodes:
                    if a_concept.nodeType == a_concept.ELEMENT_NODE:
                        if a_concept.nodeName == 'skos:ConceptScheme':
                            attr_value = a_concept.attributes.items()[0][1]
                            if attr_value == 'Unknown':
                                extra_node = n_dom.createElement('skos:hasTopConcept')
                                a_concept.appendChild(extra_node)
                                extra_node.setAttribute('rdf:resource', concept_id)
                                change_file(n_dom, transformed_file)
                                
# Each difference is written to a csv file            
header_list = ['concept 1', 'type of relation', 'concept 2']
d_file  = open(issue_file, "wb")
writer = csv.writer(d_file) 
writer.writerow(header_list)
for d in full_list_of_differnces:
    writer.writerow(d)
d_file.close()

#Each typeless concept is written to a csv file
b_file  = open(missing_file, "wb")
the_writer = csv.writer(b_file) 
for missing in typeless_concepts:
    the_writer.writerow(missing)
b_file.close()              

print datetime.now() - startTime

                 
 
