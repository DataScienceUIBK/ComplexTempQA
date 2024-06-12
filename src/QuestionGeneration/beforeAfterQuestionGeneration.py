from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import sys
import requests

# Initialize SPARQLWrapper with the endpoint URL for Wikidata
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# Ensure the script receives the correct number of arguments
if len(sys.argv) != 5:
    raise ValueError('First argument is input entity, second argument is input relation, third is SPARQL template, '
                     'fourth is question template')

# Assign command-line arguments to variables
inputEntity = sys.argv[1]
inputRelation = sys.argv[2]

# Read the SPARQL template from the provided file
with open(sys.argv[3], 'r') as file:
    SPARQL_template = file.read()

# Read the question template from the provided file
with open(sys.argv[4], 'r') as file:
    questionTemplate = file.read()

# Replace placeholders in the SPARQL template with the actual entity and relation
SPARQL_template = SPARQL_template.replace("[ENTITY]", inputEntity)
SPARQL_template = SPARQL_template.replace("[RELATION]", inputRelation)

# Set the query and return format for the SPARQLWrapper
sparql.setQuery(SPARQL_template)
sparql.setReturnFormat(JSON)

# Execute the SPARQL query and get the results
results = sparql.query().convert()

# Convert the query results to a pandas DataFrame
results_df = pd.json_normalize(results['results']['bindings'])

# Extract relevant columns from the DataFrame
queryResult = []
if 'start.value' in results_df.columns and 'end.value' in results_df.columns:
    queryResult = results_df[['itemLabel.value', 'start.value', 'end.value']]
elif 'date.value' in results_df.columns:
    queryResult = results_df[['itemLabel.value', 'date.value']]

# Retrieve the label of the input entity from Wikidata
link = f'https://www.wikidata.org/wiki/Special:EntityData/{inputEntity.split(":")[1]}.json'
outputEntity = requests.get(link).json().get('entities').get(inputEntity.split(':')[1]).get('labels').get('en').get('value')

# Initialize lists to store questions
beforeQuestion = list()
afterQuestion = list()

# Prepare before and after questions
before = None
for idx, row in queryResult.iterrows():
    item = row['itemLabel.value']
    if before is not None:
        beforeQuestion.append((item, before))
        afterQuestion.append((before, item))
    before = item

# Generate and print "before" questions
signal = "before"
for beforeTuple in beforeQuestion:
    tmpQuestionTemplate = questionTemplate.replace("[ENTITY]", outputEntity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", beforeTuple[0])
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
    print(tmpQuestionTemplate[:-1])
    print(beforeTuple[1])

# Generate and print "after" questions
signal = "after"
for afterTuple in afterQuestion:
    tmpQuestionTemplate = questionTemplate.replace("[ENTITY]", outputEntity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", afterTuple[0])
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
    print(tmpQuestionTemplate[:-1])
    print(afterTuple[1])
