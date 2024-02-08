#!/usr/bin/python

varCounter = 0

def createSingleStatment(p,r):
    global varCounter
    if varCounter == 0:
        root = r
    else:
        root = "?var" + str(varCounter-1)
    varCounter += 1
    return "    " + root + " wdt:" + p + " ?var" + str(varCounter-1) + "."

location=[("item","P17"),("P17","P571"), ("P17", "P37"),[("P17","P610"),("P610","P2044")],[("P17","P1589"),("P610","P2044")],
          [("P17","P36")],("P36","P571"), ("P36", "P37"),[("P36","P610"),("P610","P2044")],[("P17","P1589"),("P610","P2044")]]


def SPARQLGenerator(QID,pList, time=True):

    global varCounter
    query = "SELECT ?end ?date ?start"
    midQuery = "Optional {\n"
    for p in pList:
        midQuery += createSingleStatment(p,"wd:" + QID) + "\n"
    midQuery += "    }"

    timeQuery = ""

    if time:
        timeQuery = """
        Optional { wd:""" + QID + """ wdt:P582 ?end.}
        Optional { wd:""" + QID + """ wdt:P585 ?date.}
        Optional { wd:""" + QID + """ wdt:P580 ?start.}
        { wd:""" + QID + """ wdt:P585 ?w585. BIND (?w585 as ?time)} UNION { wd:""" + QID + """ wdt:P580 ?w580. BIND (?w580 as ?time)} 
        FILTER ( YEAR(?time) >= 1987 )
        FILTER ( YEAR(?time) <= 2007)"""

    for c in range(0,varCounter):
        query += " ?var" + str(c)
    query += " WHERE { """"                                         
    """+timeQuery+"""
    """+midQuery+"""
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }"""
    varCounter = 0
    return query


def SPARQLGeneratorCount(QID, pList, addQuery):
    global varCounter
    query = "SELECT ?end ?date ?start"
    midQuery = "{\n"
    for p in pList:
        midQuery += createSingleStatment(p, '?item') + "\n"
    midQuery += "    }"

    for c in range(0, varCounter):
        query += " ?var" + str(c)
    query += " WHERE { """" 
    ?item wdt:P31/wdt:P279* wd:""" + QID + """.
    Optional { ?item wdt:P582 ?end.}
    Optional { ?item wdt:P585 ?date.}
    Optional { ?item wdt:P580 ?start.}
    { ?item wdt:P585 ?w585. BIND (?w585 as ?time)} UNION { ?item wdt:P580 ?w580. BIND (?w580 as ?time)}                                           
    FILTER ( YEAR(?time) >= 1987 )
    FILTER ( YEAR(?time) <= 2007)
    """ + midQuery + """
    """ + addQuery + """
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }"""
    varCounter = 0
    return query


#print(SPARQLGenerator("Q159821",["P17","P36","P571"]))
#print(SPARQLGenerator("Q47566",["P991","P22","P569"]))