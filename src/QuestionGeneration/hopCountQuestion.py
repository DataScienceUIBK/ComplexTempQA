from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import sys
import requests
import db
import SPARQL_reader
import json
import datetime
import time
import SPARQLGenerator2
from datetime import datetime
import re
import nltk  # $ pip install nltk
from nltk.corpus import cmudict  # >>> nltk.download('cmudict')
from datetime import date


def extractQuestion(answer, id, properties,description):


    tmpQuestionTemplate = question_template_time.replace("[EVENT]", db.getNameOfEntity(id) + description)

    if answer is not None:
        json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                             ' "answer": ' + json.dumps(answer) + ',' \
                                                                                                  ' "type": ' + json.dumps(
            str(1)) + '},'
        #print(json_data)
        db.write_answer([1], tmpQuestionTemplate, [answer], [id],None,[properties[0],properties[1]], None)

    return id, answer, properties, description

def createSparqlAndQuestion(qid, properties, threshold, isHigher):
    if isHigher:
        comperator = '>'
    else:
        comperator = '<'
    sparql = SPARQLGenerator2.SPARQLGeneratorCount(qid, properties, "FILTER ( ?var" + str(len(properties) -1) + " " + comperator + " " + str(threshold) +" )")
    results_df = SPARQL_reader.readSPARQL(sparql, "")
    return len(results_df)

input_sparql_result = db.read_spraql_input()

def starts_with_vowel_sound(word, pronunciations=cmudict.dict()):
    for syllables in pronunciations.get(word, []):
        return syllables[0][-1].isdigit()  # use only the first one


def createPropertyQuestion(properties):
    ps = properties[::-1]
    string = ""
    for p in ps:
        string += db.getNameOfEntity(p) + " of the "
    return string[:-8]

def createEventDescription(qid, properties, threshold, isHigher):
    event = db.getNameOfEntity(qid)
    if starts_with_vowel_sound(event.split(' ')[0]):
        article = 'an '
    else:
        article = 'a '

    if threshold:
        comperator = ' is higher than '
    else:
        comperator = ' is lower than '

    if len(properties) == 1:
        return article + event + " with " + db.getNameOfEntity(properties[0]) + comperator + str(threshold)
    else:
        return article + event + " with " + createPropertyQuestion(properties) + comperator + str(threshold)


counter = 0
for prefix, entity, id_input, descr, pageView, input_id, sparql_id, id_sparql, template, desc_sparql in input_sparql_result:

    question_template_result = db.read_template_question_by_input(id_input)

    for id_question_template, question_template, type, method, a, b, c, d, e, f,p in question_template_result:
        properties = ["P17", "P610", "P2044"]
        if method != 5:
            continue
        answer = createSparqlAndQuestion('Q' + str(entity),properties,1000, True)

        question = question_template.replace('[EVENT]', createEventDescription('Q' + str(entity), properties, str(1000) + " meters", True))
        question = question.replace('[TIME]',  'between 1987 and 2007')

        #print(question)
        #print(answer)
        db.write_answer([7], question, [answer], [str(entity)], None, properties, [date(1987,1,1),date(2007,12,31)])

        counter += 1
        #print(counter)


