# Rijksmuseum thesaurus project

In this Github folder the Python scripts, SPARQL queries and other pieces of code used in the Master Project about the thesaurus of the Rijksmuseum done by Quinten van Langen, Master student Information Sciences at the VU Amsterdam, are stored.

## Reconstruct SKOS
The reconstruct_skos.py file contains the Adlib to Poolparty Python script that is used to transform the SKOS output of the Adlib thesaurus of the Rijksmuseum to the correct SKOS structure that can be imported into the PoolParty system.

To run the script:
```
python thesaurus/reconstruct.py
```

To run tests:
```
python -m unittest -v tests.test_thesaurus
```

## Parsing the AAT
The Parsing AAT.py file parses the Getty AAT. The current version of the code is specified to the materials found in the AAT.

To run the script:

```
python thesaurus/parsing_aat.py
```


## Analyse thesaurus
The AnalyseAdlib.py file analyze the Adlib files on different aspects (relations, labels). All these quantitative analyses are stored in xlsx files (Adlib_full.xlsx and Adlib_materials.xlsx).

To run the script:
```
python thesaurus/analyse.py
```

To run tests:
```
python -m unittest -v tests.test_thesaurus.TestThesaurusAnalysis
```

All created outputs are stored in the 'out' folder. 
