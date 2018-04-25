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

    # def test_list_concept_schemes(self):
    #     """ test if all used concept schemes are listed """
    #     concept_schemes = reconstruct_skos.list_concept_schemes(self.dom)
    #     self.assertEquals(len(concept_schemes), 1)
    #
    # def test_list_schemeless_concepts(self):
    #     """ test if all concepts without a scheme are listed """
    #     schemeless = reconstruct_skos.list_schemeless_concepts(self.dom)
    #     test_schemeless = [
    #         'http://concept.net/2',
    #         'http://concept.net/3'
    #     ]
    #     self.assertEquals(schemeless, test_schemeless)
    #
    # def test_inverse_hierarchy(self):
    #     """ test if an inverted hierarchy is created """
    #     inverse_hierarchy = reconstruct_skos.create_inverse_hierarchy(self.dom)
    #     self.assertEquals(len(inverse_hierarchy), 3)
    #
    # def test_differences_hierarchy(self):
    #     """ test if hierarchical differences are found """
    #     hierarchy = reconstruct_skos.create_inverse_hierarchy(self.dom)
    #     differences = reconstruct_skos.list_hierarchical_differences(
    #         hierarchy,
    #         self.dom
    #     )
    #     print(hierarchy)
    #     print(differences)
    #     # self.assertEquals(len(inverse_hierarchy), 3)


if __name__ == '__main__':
    unittest.main()
