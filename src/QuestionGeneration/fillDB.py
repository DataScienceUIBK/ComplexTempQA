#!/usr/bin/python

import SPARQL_reader
import db

#Q294414
#sparql_query = 'SELECT ?item ?itemLabel WHERE{?item wdt:P279?/wdt:P31? wd:Q48352 .' \
#               '  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }}'
               
sparql_query = 'SELECT ?item ?itemLabel WHERE{?item wdt:P279?/wdt:P31? wd:Q14212 . '\
                             ' FILTER ( NOT EXISTS { ?item  wdt:P576 [] } ) '\
                             ' FILTER ( ?item not in ( wd:Q9596637,wd:Q26897257,wd:Q93412501,wd:Q111364541,wd:Q14212,wd:Q23729452,wd:Q6724323,wd:Q4676862,wd:Q116357 ) ) '\
                ' SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }}'

results_df = SPARQL_reader.readSPARQL(sparql_query, "")
counter = 229
result = []
for idx, row in results_df[['item.value', 'itemLabel.value']].iterrows():
    value = str(row['itemLabel.value'])
    if 1:
    #if value.__contains__("monarch") or value.__contains__("Monarch"):
    #if value.__contains__("Chancellor") or value.__contains__("Governor") or value.__contains__("President"):
        result.append(("Q",row['item.value'].rsplit("/",1)[1][1:],counter,row['itemLabel.value'].replace("'","")))
        counter += 1

print("fill database")
db.insert_input(result)
