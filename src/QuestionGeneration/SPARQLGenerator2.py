#!/usr/bin/python

# Initialize a counter to track the number of variables created
varCounter = 0

def createSingleStatement(p, r):
    """
    Create a single SPARQL statement based on the property and root node.

    Args:
        p (str): The property to query.
        r (str): The root node for the query.

    Returns:
        str: A formatted SPARQL statement.
    """
    global varCounter
    if varCounter == 0:
        root = r
    else:
        root = "?var" + str(varCounter - 1)
    varCounter += 1
    return "    " + root + " wdt:" + p + " ?var" + str(varCounter - 1) + "."

# Sample location data with various property pairs
location = [
    ("item", "P17"), ("P17", "P571"), ("P17", "P37"),
    [("P17", "P610"), ("P610", "P2044")],
    [("P17", "P1589"), ("P610", "P2044")],
    [("P17", "P36")], ("P36", "P571"), ("P36", "P37"),
    [("P36", "P610"), ("P610", "P2044")],
    [("P17", "P1589"), ("P610", "P2044")]
]

def SPARQLGenerator(QID, pList, time=True):
    """
    Generate a SPARQL query for the given QID and property list.

    Args:
        QID (str): The Wikidata QID to query.
        pList (list): List of properties to include in the query.
        time (bool): Flag to include time constraints.

    Returns:
        str: The generated SPARQL query.
    """
    global varCounter
    query = "SELECT ?end ?date ?start"
    midQuery = "Optional {\n"
    for p in pList:
        midQuery += createSingleStatement(p, "wd:" + QID) + "\n"
    midQuery += "    }"

    timeQuery = ""
    if time:
        timeQuery = f"""
        Optional {{ wd:{QID} wdt:P582 ?end.}}
        Optional {{ wd:{QID} wdt:P585 ?date.}}
        Optional {{ wd:{QID} wdt:P580 ?start.}}
        {{ wd:{QID} wdt:P585 ?w585. BIND (?w585 as ?time)}} UNION {{ wd:{QID} wdt:P580 ?w580. BIND (?w580 as ?time)}}
        FILTER ( YEAR(?time) >= 1987 )
        FILTER ( YEAR(?time) <= 2007)"""

    for c in range(varCounter):
        query += " ?var" + str(c)
    query += f" WHERE {{ \n{timeQuery}\n{midQuery}\n"
    query += """
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }"""
    varCounter = 0
    return query

def SPARQLGeneratorCount(QID, pList, addQuery):
    """
    Generate a SPARQL query to count instances of the given QID with additional properties.

    Args:
        QID (str): The Wikidata QID to query.
        pList (list): List of properties to include in the query.
        addQuery (str): Additional query string to append.

    Returns:
        str: The generated SPARQL query.
    """
    global varCounter
    query = "SELECT ?end ?date ?start"
    midQuery = "{\n"
    for p in pList:
        midQuery += createSingleStatement(p, '?item') + "\n"
    midQuery += "    }"

    for c in range(varCounter):
        query += " ?var" + str(c)
    query += f" WHERE {{ \n"
    query += f"?item wdt:P31/wdt:P279* wd:{QID}.\n"
    query += """
    Optional { ?item wdt:P582 ?end.}
    Optional { ?item wdt:P585 ?date.}
    Optional { ?item wdt:P580 ?start.}
    { ?item wdt:P585 ?w585. BIND (?w585 as ?time)} UNION { ?item wdt:P580 ?w580. BIND (?w580 as ?time)}
    FILTER ( YEAR(?time) >= 1987 )
    FILTER ( YEAR(?time) <= 2007)
    """ + midQuery + "\n" + addQuery + """
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }"""
    varCounter = 0
    return query
