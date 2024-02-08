#!/usr/bin/python

varList = list()

def createSingleStatment(root,p):
    varList.append(p)
    return "?" + root + " wdt:" + p + " ?" + p + "."

def createMulitStatment(pList):
    resultQuery = ""
    for p in pList:
        if type(p) is list:
            resultQuery += createMulitStatment(p)
        else:
            resultQuery += "Optional {" + createSingleStatment(p[0],p[1]) + "}\n"
    return resultQuery

def createPointStatment():
    varList.append("P1351")
    return """{ SELECT (SUM(?a) as ?P1923) ?item WHERE {
    ?item p:P1923   ?s  .  # ?s is the the statement node
           ?s  pq:P1351 ?a  .  # this is an attribute (a qualifier) 
     } group by ?item
   }
    """

location=[("item","P17"),("P17","P571"), ("P17", "P37"),[("P17","P610"),("P610","P2044")],[("P17","P1589"),("P610","P2044")],
          [("P17","P36")],("P36","P571"), ("P36", "P37"),[("P36","P610"),("P610","P2044")],[("P17","P1589"),("P610","P2044")]]


def SPARQLGenerator(QID):

    query = "SELECT DISTINCT ?item ?end ?date ?start"

    midQuery = "Optional {" + createMulitStatment(location) + "}"
    midQuery += "Optional {" + createPointStatment() + "}"

    for v in varList:
        query += " ?" + v
    query += " WHERE { ?item wdt:P31/wdt:P279* wd:" + QID + """ 
    Optional { ?item wdt:P582 ?end.}
    Optional { ?item wdt:P585 ?date.}
    Optional { ?item wdt:P580 ?start.}
    { ?item wdt:P585 ?w585. BIND (?w585 as ?time)} UNION { ?item wdt:P580 ?w580. BIND (?w580 as ?time)}                                           
    FILTER ( YEAR(?time) >= 1987 )
    FILTER ( YEAR(?time) <= 2007)
    """+midQuery+"""
    
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    ORDER BY ASC(?time)"""

    return query


print(SPARQLGenerator("Q32096"))