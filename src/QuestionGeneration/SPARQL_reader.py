#!/usr/bin/python

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import time

def SPARQL_Exec(query):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    # sparql = SPARQLWrapper("http://127.0.0.1:9999/bigdata/namespace/wdq/sparql")

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    return sparql.query().convert()


def readSPARQL(SPARQL_template, inputEntity):


    SPARQL_template = SPARQL_template.replace("[ENTITY]", inputEntity)

    try:
        time.sleep(20)
        results = SPARQL_Exec(SPARQL_template)
    except:
        time.sleep(60)
        try:
            results = SPARQL_Exec(SPARQL_template)
        except:
            time.sleep(60)
            results = SPARQL_Exec(SPARQL_template)

    return pd.json_normalize(results['results']['bindings'])


def checkSPARQLEntity(catId, p, attr, year=None):

    attrQuery = ""
    for a in attr:
        attrQuery += f"""
            ?item wdt:{p} wd:{a}.
            """
    sparqlQuery = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        SELECT ?item
        WHERE {{
            ?item wdt:P31 wd:{catId}.
            {{{{ ?item wdt:P571 ?w585. BIND (?w585 as ?time)}} UNION {{ ?item wdt:P569 ?w580. BIND (?w580 as ?time)}} UNION {{ ?item wdt:P577 ?w577. BIND (?w577 as ?time)}}}}

    """
    sparqlQuery += attrQuery
    if year is not None:
        sparqlQuery += f"""
                FILTER(YEAR(?time) = {year})
            
        """
    sparqlQuery += "}"
    #print(sparqlQuery)
    try:
        time.sleep(12)
        results = SPARQL_Exec(sparqlQuery)
    except:
        time.sleep(60)
        try:
            results = SPARQL_Exec(sparqlQuery)
        except:
            time.sleep(60)
            results = SPARQL_Exec(sparqlQuery)

    return pd.json_normalize(results['results']['bindings'])


def checkSPARQL(isInt, catId, year, p, attr, country=None):
    if isInt:
        attrQuery = f"""
            ?item wdt:{p} ?value.
            FILTER(?value = {attr})
    """
    else:
        attrQuery = f"""
            ?item wdt:{p} wd:{attr}.
            """
    sparqlQuery = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        SELECT ?item
        WHERE {{
            ?item wdt:P31 wd:{catId}.
            ?item wdt:P585 ?date.
            
    """
    sparqlQuery += attrQuery
    if country:
        sparqlQuery += f"    ?item wdt:P17 wd:{country}."

    sparqlQuery += f"""
            FILTER(YEAR(?date) = {year})
        }}
    """
    #print(sparqlQuery)
    try:
        time.sleep(12)
        results = SPARQL_Exec(sparqlQuery)
    except:
        time.sleep(60)
        try:
            results = SPARQL_Exec(sparqlQuery)
        except:
            time.sleep(60)
            results = SPARQL_Exec(sparqlQuery)

    return pd.json_normalize(results['results']['bindings'])
