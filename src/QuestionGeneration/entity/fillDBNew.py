#!/usr/bin/python

import SPARQL_reader
import db
import math

# Q294414
# sparql_query = 'SELECT ?item ?itemLabel WHERE{?item wdt:P279?/wdt:P31? wd:Q48352 .' \
#               '  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }}'

# sparql_query = 'SELECT distinct ?item ?itemLabel ?country WHERE{?item wdt:P279?/wdt:P31? wd:Q18123741. ' \
#                ' OPTIONAL{?country wdt:P17? ?item. }'\
#                           ' SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }}'


sparql_queries = [
    '''
    SELECT ?item ?itemLabel ?startDate
WHERE {
  ?item wdt:P31 wd:Q11424;             # Movies
    wdt:P577 ?startDate.  # Publication date
   ?item wdt:P345 ?imdbId.
  
  FILTER (YEAR(?startDate) >= 1987 && YEAR(?startDate) <= 2007)
 FILTER ( ?item not in ( wd:Q8907 ) )

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC(?item)
    ''',
    '''
   SELECT ?item ?itemLabel ?startDate
WHERE {
  ?item wdt:P31 wd:Q571;             # Books
        wdt:P577 ?startDate.  # Publication date

  FILTER (YEAR(?startDate) >= 1987 && YEAR(?startDate) <= 2007)
    ?item rdfs:label ?itemLabel.
  FILTER(LANGMATCHES(LANG(?itemLabel), "en"))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC(?item)

    ''',
    '''
    SELECT ?item ?itemLabel ?startDate ?country
WHERE {
  ?item wdt:P1435 wd:Q9259;
        wdt:P571 ?startDate.
  
 FILTER(YEAR(?startDate)> 1987)
 FILTER(YEAR(?startDate)< 2007)
   OPTIONAL{?item wdt:P17 ?country. }
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
    ?item rdfs:label ?itemLabel.
  }
}
ORDER BY DESC(?item)
    '''
    ,
    '''
    SELECT distinct ?item ?itemLabel ?startDate ?endDate ?country 
    WHERE{
    ?item wdt:P279?/wdt:P31? wd:Q811979. #building
                                                ?item wdt:P571 ?startDate.
                                                FILTER(YEAR(?startDate)> 1987)
                                                FILTER(YEAR(?startDate)< 2007)
                                                OPTIONAL{?item wdt:P17 ?country. }
                                                OPTIONAL{
                                                  ?item wdt:P576 ?endDate.
                                                FILTER(YEAR(?endDate)> 1987)
                                                FILTER(YEAR(?endDate)< 2007)
                                              } SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }}
                                              ORDER BY DESC(?item)
    '''
    ,
    '''
       SELECT ?item ?itemLabel ?startDate ?country (GROUP_CONCAT(DISTINCT ?founder; separator=", ") AS ?founders) WHERE { #company
  ?item wdt:P112 ?founder.
  ?item wdt:P571 ?startDate .
  FILTER (YEAR(?startDate) >= 1987 && YEAR(?startDate) <= 2007)
  FILTER EXISTS { ?item wdt:P414|wdt:P249 []. }
  OPTIONAL{?item wdt:P17 ?country. }
  OPTIONAL { ?founder rdfs:label ?founderLabel. FILTER(LANG(?founderLabel) = "en"). }
  OPTIONAL { ?item wdt:P2403|wdt:P2137|wdt:P2139|wdt:P2226|wdt:P2295 ?money. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?item ?itemLabel ?startDate ?country
ORDER BY DESC(?item)
    '''
]

cat = ['movie', 'book', 'unesco','building','company']  # Category corresponding to each query result

result = []

for i, sparql_query in enumerate(sparql_queries):
    results_df = SPARQL_reader.readSPARQL(sparql_query, "")

    labelRows = ['item.value', 'itemLabel.value', 'startDate.value', ]
    if 'country.value' in results_df.columns:
        labelRows.append('country.value')
    if 'endDate.value' in results_df.columns:
        labelRows.append('endDate.value')
    for idx, row in results_df[labelRows].iterrows():
        value = row['item.value'].rsplit("/", 1)[1][1:]
        item_label = row['itemLabel.value'].replace("'", "").replace('"', '')
        start_date = row['startDate.value']
        category = cat[i]

        # Check if 'country.value' exists
        if 'country.value' in row and not (type(row['country.value']) == float and math.isnan(row['country.value'])):
            country_value = row['country.value'].rsplit("/", 1)[1][1:]
        else:
            country_value = None

        # Check if 'endDate.value' exists
        if 'endDate.value' in row and not (type(row['endDate.value']) == float and math.isnan(row['endDate.value'])):
            end_date = row['endDate.value']
        else:
            end_date = None

        if len(result) > 0 and result[-1][0] == value:
            result[-1] = (value, item_label, start_date, category, country_value, end_date)
        else:
            result.append((value, item_label, start_date, category, country_value, end_date))


# Create the INSERT INTO query
insert_values = []
for item in result:
    entity_id, name, start_date, category, country, end_date = item
    # Handle NULL values for country and end_date
    if country is None:
        country = 'NULL'
    else:
        country = f"'{country}'"
    if end_date is None :
        end_date = 'NULL'
    else:
        end_date = f"'{end_date}'"

    # Format the values for the query
    insert_values.append(f"({entity_id}, '{name}', '{start_date}', '{category}', {country}, {end_date})")

# Combine all the values into a single string
values_str = ', '.join(insert_values)

# Create the final INSERT INTO query
query = f'INSERT INTO "Entities" ("EntityID", "Name", "StartDate", "category", "Country", "EndDate") VALUES {values_str};'

# Assuming you have a function called db.write_db to execute the query
db.write_db(query)

print("fill database")

# print("fill database")
# query = 'Insert Into "Entities" ("EntityID","Name","StartDate", category) VALUES ' + str(result).strip('[]') + ';'


# db.write_db(query)
