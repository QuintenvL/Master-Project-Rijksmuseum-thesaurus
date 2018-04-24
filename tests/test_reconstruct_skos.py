"""
Unittests for thesaurus analysis
"""
import os
import random
import unittest
from xml.dom.minidom import getDOMImplementation
from thesaurus import reconstruct_skos


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
        node1 = self.dom.createElement('skos:Concept')
        node1.setAttribute('rdf:about', 'http://concept.net/1')
        scheme1 = self.dom.createElement('skos:inScheme')
        scheme1.setAttribute('rdf:resource', 'http://concept_scheme.net/1')
        node1.appendChild(scheme1)
        top_element.appendChild(node1)
        node2 = self.dom.createElement('skos:Concept')
        node2.setAttribute('rdf:about', 'http://concept.net/2')
        top_element.appendChild(node2)
        node3 = self.dom.createElement('skos:ConceptScheme')
        node3.setAttribute('rdf:about', 'http://concept_scheme.net/1')
        top_element.appendChild(node3)


    def test_list_concepts(self):
        """ list concepts and make sure only skos concepts are listed """
        concepts = reconstruct_skos.list_concepts(self.dom)
        test_concepts = ['http://concept.net/1', 'http://concept.net/2']
        self.assertEqual(concepts, test_concepts)

    def test_list_concept_schemes(self):
        """ test if all used concept schemes are listed """
        concept_schemes = reconstruct_skos.list_concept_schemes(self.dom)
        self.assertEquals(len(concept_schemes), 1)

    def test_list_schemeless_concepts(self):
        """ test if all concepts without a scheme are listed """
        schemeless = reconstruct_skos.list_schemeless_concepts(self.dom)
        self.assertEquals(schemeless, ['http://concept.net/2'])


if __name__ == '__main__':
    unittest.main()
