'''
Created on 13 mrt. 2018

@author: Gebruiker
'''
import os
import csv
from xml.dom.minidom import parse
from shutil import copyfile

orginial_file = 'R_thesaurus_material_20180221.rdf'
transformed_file = 'Material_Transformed.rdf'
issue_file = 'differences_file.csv'

os.chdir('../thesaurus_export')
dom = parse(orginial_file)
o_rdf = dom.childNodes.item(0)
scheme_values = []
hierarchy_dict = {}
for o_concept in o_rdf.childNodes:
    if o_concept.nodeType == o_concept.ELEMENT_NODE:
        o_concept_id = o_concept.attributes.items()[0][1]
        for o_property in o_concept.childNodes:
            if o_property.nodeType == o_property.ELEMENT_NODE:
                if o_property.nodeName == 'skos:inScheme':
                    property_attr = o_property.attributes.items()[0][1]
                    if property_attr not in scheme_values:
                        scheme_values.append(property_attr)
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

print hierarchy_dict
                         
# print scheme_values
                    
#Scheme name from the attribute = [42:]


copyfile(orginial_file, transformed_file)
  
# print type(parse('transformed.rdf'))
full_list_of_differnces = []
n_dom = parse(transformed_file)
childs = n_dom.childNodes
rdf = childs.item(0)
for schemes in scheme_values:
    scheme_node = n_dom.createElement('skos:ConceptScheme')
    rdf.appendChild(scheme_node)
    scheme_node.setAttribute('rdf:about', schemes)
    concept_node = n_dom.createElement('dct:title')
    scheme_node.appendChild(concept_node)
    concept_node.setAttribute('xml:lang', 'en')
    text_node = n_dom.createTextNode(schemes[42:])
    concept_node.appendChild(text_node)
    xml_file = open(transformed_file, "w")
    xml_file.write(n_dom.toprettyxml().encode("utf-8"))
    xml_file.close()
for concept in rdf.childNodes:
    if concept.nodeName == 'skos:ConceptScheme':
        continue
    if concept.nodeType == concept.ELEMENT_NODE:
        concept_id = concept.attributes.items()[0][1]
#         print concept.attributes.items()[0][1]
#         print concept.nodeName
        concept_properties = concept.childNodes
        property_dict = {}
        for property in concept_properties:
            if property.nodeType == property.ELEMENT_NODE:
                if property.hasChildNodes():
                    childs = property.childNodes # property with value have a child node that contain the value. Example: prefLabel = goud
                elif property.nodeName == 'skos:topConceptOf':
                    t = property
                else:
                    label = property.nodeName
                    attribute_value = property.attributes.items()[0][1]
#                     print property.attributes.items()[0][1]
                    if label in property_dict:
                        property_dict[label].append(attribute_value)
                    else:                        
                        property_dict[label] = [attribute_value]
        print concept_id ,property_dict
        hierarchy_labels = ['skos:broader', 'skos:narrower', 'skos:related']
        if concept_id in hierarchy_dict:
            for h_label in hierarchy_labels:
                if h_label in property_dict and h_label in hierarchy_dict[concept_id]:
                    length_property = len(property_dict[h_label])
                    difference = list(set(property_dict[h_label]) - set(hierarchy_dict[concept_id][h_label]))
                    if difference != []:
                        difference_list = [concept_id, h_label, difference]
                        full_list_of_differnces.append(difference_list)
#                         print difference
#                         print length_property
                        for prop_differ in difference:
                            property_dict[h_label].remove(prop_differ)
                            if len(property_dict[h_label]) < 1:
                                del property_dict[h_label]
                            for w_property in concept.childNodes:
                                if w_property.nodeType == w_property.ELEMENT_NODE:
                                    if w_property.nodeName == h_label and w_property.attributes.items()[0][1] == prop_differ:
                                        concept.removeChild(w_property)
                                        xml_file = open(transformed_file, "w")
                                        xml_file.write(n_dom.toprettyxml().encode("utf-8"))
                                        xml_file.close()
                elif h_label not in property_dict and h_label in hierarchy_dict[concept_id]:
                    difference_list = [concept_id, h_label,hierarchy_dict[concept_id][h_label]]
                    full_list_of_differnces.append(difference_list)
                elif h_label in property_dict and h_label not in hierarchy_dict[concept_id]:
                    difference_list = [concept_id, h_label,property_dict[h_label]]
                    full_list_of_differnces.append(difference_list)
                else:
                    continue
#         print concept_id, property_dict
        if 'skos:broader' not in property_dict:
            for scheme in property_dict['skos:inScheme']:
                new_node = n_dom.createElement('skos:topConceptOf')
                concept.appendChild(new_node)
                new_node.setAttribute('rdf:resource', scheme)
#                 xml_file = open(transformed_file, "w")
#                 xml_file.write(n_dom.toprettyxml().encode("utf-8"))
#                 xml_file.close()
                for a_concept in rdf.childNodes:
                    if a_concept.nodeType == a_concept.ELEMENT_NODE:
                        if a_concept.nodeName == 'skos:ConceptScheme':
                            attr_value = a_concept.attributes.items()[0][1]
                            if attr_value == scheme:
                                extra_node = n_dom.createElement('skos:hasTopConcept')
                                a_concept.appendChild(extra_node)
                                extra_node.setAttribute('rdf:resource', concept_id)
                                xml_file = open(transformed_file, "w")
                                xml_file.write(n_dom.toprettyxml().encode("utf-8"))
                                xml_file.close()
        
header_list = ['concept 1', 'type of relation', 'concept 2']
d_file  = open(issue_file, "wb")
writer = csv.writer(d_file) 
writer.writerow(header_list)
for d in full_list_of_differnces:
    writer.writerow(d)
d_file.close()          
            

                 
 
