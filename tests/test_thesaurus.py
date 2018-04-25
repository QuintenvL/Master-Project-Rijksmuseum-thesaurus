"""
Unittests for thesaurus analysis
"""
import os
import random
import unittest
from xml.dom.minidom import getDOMImplementation
from thesaurus import reconstruct, analyse


class TestThesaurusAnalysis(unittest.TestCase):
    """ TestCase for basic thesaurus analysis functions """

    def setUp(self):
        # create SKOS XML dom
        impl = getDOMImplementation()
        self.dom = impl.createDocument(
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdf:RDF',
            None
        )
        top_element = self.dom.documentElement
        top_element.setAttributeNS(
            "xmls",
            "xmlns:rdf",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        )
        top_element.setAttributeNS(
            "xmls",
            "xmlns:skos",
            "http://www.w3.org/2004/02/skos/core#"
        )
        top_element.setAttributeNS(
            "xmls",
            "xmlns:dct",
            "http://purl.org/dc/terms/"
        )
        # Add first concept
        node1 = self.dom.createElement('skos:Concept')
        node1.setAttribute('rdf:about', 'http://concept.net/1')
        scheme1 = self.dom.createElement('skos:inScheme')
        scheme1.setAttribute('rdf:resource', 'http://concept_scheme.net/1')
        node1.appendChild(scheme1)
        narrower1 = self.dom.createElement('skos:narrower')
        narrower1.setAttribute('rdf:resource', 'http://concept.net/2')
        node1.appendChild(narrower1)
        top_element.appendChild(node1)
        # Add second concept
        node2 = self.dom.createElement('skos:Concept')
        node2.setAttribute('rdf:about', 'http://concept.net/2')
        broader1 = self.dom.createElement('skos:broader')
        broader1.setAttribute('rdf:resource', 'http://concept.net/3')
        node2.appendChild(broader1)
        top_element.appendChild(node2)
        # Add third concept
        node3 = self.dom.createElement('skos:Concept')
        node3.setAttribute('rdf:about', 'http://concept.net/3')
        related1 = self.dom.createElement('skos:related')
        related1.setAttribute('rdf:resource', 'http://concept.net/1')
        node3.appendChild(related1)
        top_element.appendChild(node3)
        # Add first concept scheme
        node3 = self.dom.createElement('skos:ConceptScheme')
        node3.setAttribute('rdf:about', 'http://concept_scheme.net/1')
        top_element.appendChild(node3)


    def test_list_concepts(self):
        """ List concepts and make sure only SKOS concepts are listed. """
        concepts = analyse.list_concepts(self.dom)
        test_concepts = [
            'http://concept.net/1',
            'http://concept.net/2',
            'http://concept.net/3'
        ]
        self.assertEqual(concepts, test_concepts)

    def test_list_concept_schemes(self):
        """ Test if all referenced concept schemes are listed. """
        concept_schemes = analyse.referenced_concept_schemes(self.dom)
        test_schemes = ['http://concept_scheme.net/1']
        self.assertEquals(concept_schemes, test_schemes)

    def test_list_schemeless_concepts(self):
        """ Test if all concepts without a scheme are listed. """
        schemeless = analyse.list_schemeless_concepts(self.dom)
        test_schemeless = [
            'http://concept.net/2',
            'http://concept.net/3'
        ]
        self.assertEquals(schemeless, test_schemeless)

    def test_inverse_hierarchy(self):
        """ Test if an inverted hierarchy is properly created. """
        inverse_hierarchy = analyse.create_inverse_hierarchy(self.dom)
        self.assertEquals(len(inverse_hierarchy), 3)

    def test_property_dict(self):
        """ Test if hierarchical properties are extracted. """
        node = self.dom.childNodes.item(0).childNodes.item(0)
        property_dict = analyse.hierarchical_properties_dict(node)
        test_dict = {'skos:narrower': ['http://concept.net/2']}
        self.assertEquals(property_dict, test_dict)

    def test_missing_concepts(self):
        """ Test if outward difference is returned. """
        concept1 = 'http://concept.net/1'
        props1 = {'skos:broader': ['http://concept.net/3']}
        i_props1 = {'skos:broader': [
            'http://concept.net/2',
            'http://concept.net/5'
        ]}
        props2 = {
            'skos:broader': ['http://concept.net/3'],
            'skos:narrower': ['http://concept.net/4']
        }
        i_props2 = {
            'skos:broader': ['http://concept.net/2'],
            'skos:narrower': ['http://concept.net/5']
        }
        missing1 = analyse.outward_difference(concept1, props1, i_props1)

        self.assertEquals(len(missing1), 1)
        missing2 = analyse.outward_difference(concept1, props2, i_props2)
        self.assertEquals(len(missing2), 2)

    def test_differences_hierarchy(self):
        """ Test if hierarchical differences are found. """
        outward = analyse.missing_outward_references(self.dom)

        self.assertEquals(len(outward), 3)


if __name__ == '__main__':
    unittest.main()
