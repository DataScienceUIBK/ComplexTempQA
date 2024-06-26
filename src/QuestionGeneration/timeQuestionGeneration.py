from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import sys
import requests
import db

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
    queryResult = results_df[['item.value', 'start.value', 'end.value']]
elif 'date.value' in results_df:
    queryResult = results_df[['item.value', 'date.value']]

link = 'https://www.wikidata.org/wiki/Special:EntityData/' + inputEntity.split(':')[1] + '.json'
outputEntity = requests.get(link).json().get('entities').get(inputEntity.split(':')[1]).get('labels').get('en').get(
    'value')

resultQuestion = dict()
for idx, row in queryResult.iterrows():
    date = ""
    item = row['item.value']
    if 'start.value' and 'end.value' in results_df:
        startYear = int(row['start.value'][:4])
        endYear = int(row['end.value'][:4])
        date = str(startYear) + " - " + str(endYear)
    elif 'date.value' in results_df:
        date = int(row['date.value'][:4])
    dateList = list()
    if item in resultQuestion:
        dateList = resultQuestion[item]
    dateList.append(date)
    resultQuestion.update({item: dateList})

for key in resultQuestion:
    tmpQuestionTemplate = questionTemplate.replace("[ENTITY]", outputEntity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", db.getNameOfEntity(key))
    db.write_answer([6], tmpQuestionTemplate, [db.getNameOfEntity(resultQuestion[key])], ['Q' + str(inputEntity.split(':')[1])], [key], None, None)
