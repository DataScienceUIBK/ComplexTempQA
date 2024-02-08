from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

sparql.setQuery("""
SELECT ?itemLabel ?start ?end WHERE {

   ?item wdt:P31 wd:Q5 .
   ?item p:P39 ?position_held_statement .
   ?position_held_statement ps:P39 wd:Q887010 .
  
   ?position_held_statement pq:P580 ?start .
   ?position_held_statement pq:P582 ?end .

  # filter by start date here
  FILTER(year(?end) > 1987)
  FILTER(year(?start) < 2007)

   SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
   }

 } ORDER BY ?start
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

results_df = pd.json_normalize(results['results']['bindings'])
results_df[['start.value', 'end.value', 'itemLabel.value']].head()

#print(results_df[['itemLabel.value', 'start.value', 'end.value']].head())

queryResult = results_df[['itemLabel.value', 'start.value', 'end.value']].head()

resultQuestion = list()
for i in range(1987,2008):
	result = []
	for idx,row in queryResult.iterrows():
		startYear = int(row['start.value'][:4])
		endYear = int(row['end.value'][:4])
		if startYear <= i and i <= endYear:
			result.append(row['itemLabel.value'])
	resultQuestion.append((i,result))


for year, person in resultQuestion:
	#print("Who was President in " + str(year) + "?")
	print("Who was Governor of California  in " + str(year) + "?")
	print(person)
