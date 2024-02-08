from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import sys
import requests

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

if len(sys.argv) != 5:
    raise ValueError('First agrument is input entity, second argument is input relation, third is SPARQL template, '
                     'fourth is question template')

inputEntity = sys.argv[1]
inputRelation = sys.argv[2]
SPARQL_templateFile = open(sys.argv[3])
SPARQL_template = SPARQL_templateFile.read()
SPARQL_templateFile.close()
questionTemplateFile = open(sys.argv[4])
questionTemplate = questionTemplateFile.read()
questionTemplateFile.close()

SPARQL_template = SPARQL_template.replace("[ENTITY]", inputEntity)
SPARQL_template = SPARQL_template.replace("[RELATION]", inputRelation)

sparql.setQuery(SPARQL_template)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

results_df = pd.json_normalize(results['results']['bindings'])
queryResult = []
if 'start.value' and 'end.value' in results_df:
    queryResult = results_df[['itemLabel.value', 'start.value', 'end.value']]
elif 'date.value' in results_df:
    queryResult = results_df[['itemLabel.value', 'date.value']]

link = 'https://www.wikidata.org/wiki/Special:EntityData/' + inputEntity.split(':')[1] + '.json'
outputEntity = requests.get(link).json().get('entities').get(inputEntity.split(':')[1]).get('labels').get('en').get(
    'value')

beforeQuestion = list()
afterQuestion = list()

before = None
for idx, row in queryResult.iterrows():
    item = row['itemLabel.value']
    if before is not None:
        beforeQuestion.append((item,before))
        afterQuestion.append((before,item))
    before = item

signal = "before"
for beforeTuple in beforeQuestion:
    tmpQuestionTemplate = questionTemplate.replace("[ENTITY]", outputEntity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", beforeTuple[0])
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
    print(tmpQuestionTemplate[:-1])
    print(beforeTuple[1])

signal = "after"
for afterTuple in afterQuestion:
    tmpQuestionTemplate = questionTemplate.replace("[ENTITY]", outputEntity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", afterTuple[0])
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
    print(tmpQuestionTemplate[:-1])
    print(afterTuple[1])


