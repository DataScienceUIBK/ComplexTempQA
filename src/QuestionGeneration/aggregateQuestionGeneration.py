from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import sys
import requests

# Initialize the SPARQLWrapper with the Wikidata SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# Check if the correct number of arguments is provided
if len(sys.argv) != 5:
    raise ValueError('First argument is input entity, second argument is input relation, third is SPARQL template, '
                     'fourth is question template')

# Read input arguments
inputEntity = sys.argv[1]
inputRelation = sys.argv[2]

# Read the SPARQL template file
with open(sys.argv[3], 'r') as file:
    SPARQL_template = file.read()

# Read the question template file
with open(sys.argv[4], 'r') as file:
    questionTemplate = file.read()

# Replace placeholders in the SPARQL template
SPARQL_template = SPARQL_template.replace("[ENTITY]", inputEntity)
SPARQL_template = SPARQL_template.replace("[RELATION]", inputRelation)

# Set the query and return format for SPARQLWrapper
sparql.setQuery(SPARQL_template)
sparql.setReturnFormat(JSON)

# Execute the SPARQL query and convert the results to a pandas DataFrame
results = sparql.query().convert()
results_df = pd.json_normalize(results['results']['bindings'])

# Extract relevant columns from the results
queryResult = []
if 'start.value' in results_df.columns and 'end.value' in results_df.columns:
    queryResult = results_df[['itemLabel.value', 'start.value', 'end.value']]
elif 'date.value' in results_df.columns:
    queryResult = results_df[['itemLabel.value', 'date.value']]

# Get the label of the input entity from Wikidata
link = f'https://www.wikidata.org/wiki/Special:EntityData/{inputEntity.split(":")[1]}.json'
outputEntity = requests.get(link).json().get('entities').get(inputEntity.split(':')[1]).get('labels').get('en').get('value')

# Prepare the results for the question template
resultQuestion = {}
for idx, row in queryResult.iterrows():
    item = row['itemLabel.value']
    count = resultQuestion.get(item, 0) + 1
    resultQuestion[item] = count

# Print the formatted questions
for key, count in resultQuestion.items():
    tmpQuestionTemplate = questionTemplate.replace("[ENTITY]", outputEntity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", key)
    print(tmpQuestionTemplate[:-1])
    print(count)
