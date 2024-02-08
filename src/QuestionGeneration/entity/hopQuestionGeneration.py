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

entities = db.read_db('SELECT "EntityID", "Name", category FROM "Entities" order by "EntityID"')

question_template_time = "What was the [P2] of the [P1] of [ENTITY]?"
question_template_unit = "What was the [P2] of the [P1] of [ENTITY] in meter?"

question_template_compare_yn = "Comparing [P1], has [ENTITY1] [COMPARE] [P2] than [ENTITY2]?"
question_template_compare = "Comparing [P1] of [ENTITY1] and [ENTITY2], which one has a [COMPARE] [P2]?"

def prefix(cat):
    if cat == 'person':
        return cat
    elif cat == 'unesco':
        return "the " + cat
    else:
        return "the " + cat
def extractQuestion(result, id, properties,cat):
    answer = None
    if len(result[0]) <= 21:
        tmpQuestionTemplate = question_template_time.replace("[P1]", db.getNameOfEntity(properties[0]))
    else:
        tmpQuestionTemplate = question_template_unit.replace("[P1]", db.getNameOfEntity(properties[0]))
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", db.getNameOfEntity(properties[1]))
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY]", prefix(cat) + " " + db.getNameOfEntity(id))
    if len(result[0]) <= 21:
        answer = result[0][:10]
    else:
        max = 0
        min = 0
        found = False
        for r in result:
            if r[31] == 'Q':
                if db.entityHasProperty(r[31:], "P2044"):
                    answer =  db.getIntAttributeOfEntity(r[31:],"P2044")
                    if max < answer:
                        max = answer
                    if min > answer:
                        min = answer
                    found = True
        if found:
            if tmpQuestionTemplate.__contains__("highest"):
                answer = max
            else:
                answer = min
    if answer is not None:
        json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                             ' "answer": ' + json.dumps(answer) + ',' \
                                                                                                  ' "type": ' + json.dumps(
            str(1)) + '},'
        #print(json_data)
        #db.write_answer([2], tmpQuestionTemplate, [answer], [str(id)],None,[str(properties[0]),str(properties[1])], None)#['1987-01-01', '2007-12-31'])

    return id, answer, properties, cat


def createSparqlAndQuestion(qid, properties, cat):
    sparql = SPARQLGenerator2.SPARQLGenerator(qid, properties, False)
    #print(sparql)
    results_df = SPARQL_reader.readSPARQL(sparql, "")
    #print(results_df)
    if "var1.value" in results_df:
        return extractQuestion(results_df["var1.value"], qid, properties,cat)
    return None


eventAnswer = list()


def appendIfNotNone(item):
    if item:
        eventAnswer.append(item)


print("{\n")

#try:
if True:
    for id, name, cat in entities:

        properties = [["P19", "P571"],["P19", "P2044"],["P19", "P610"],["P19", "P1589"],["P22","P19"],["P22","P569"],["P25","P19"],["P25","P569"],#person
                      ["P57","P19"],["P57","P569"], #movie
                      ["P50","P19"],["P50","P569"], #book
                      ["P17", "P610"],["P17", "P1589"]] #else

        for prop in properties:
            if cat == 'movie' and all(p not in ["P57"] for p in prop):
                continue
            elif cat == 'book' and all(p not in ["P50"] for p in prop):
                continue
            elif cat == 'person' and all(p not in ["P19", "P22", "P25"] for p in prop):
                continue
            else:
                if all(p not in ["P17"] for p in prop):
                    continue

            appendIfNotNone(createSparqlAndQuestion('Q' + str(id), prop, cat))


#except:
#    x = 1

for id, answer, properties, cat in eventAnswer:
    for id2, answer2, properties2, cat2 in eventAnswer:
        if id != id2 and properties == properties2 and answer is not None and answer2 is not None:
            if re.fullmatch("\\d\\d\\d\\d-\\d\\d-\\d\\d",str(answer)) is not None:
                if answer[0] == '-' or answer2 [0] == '-':
                    continue
                dateAnswer = datetime.strptime(answer, "%Y-%m-%d")
                dateAnswer2 = datetime.strptime(answer2, "%Y-%m-%d")

                curAnswer = id
                if dateAnswer2 > dateAnswer:
                    curAnswer = id2
                compareHelper = ("an earlier","a later")
            else:
                curAnswer = id
                if answer2 > answer:
                    curAnswer = id2
                compareHelper = ("a lower", "a higher")

            event1 = db.getNameOfEntity(id)
            event2 = db.getNameOfEntity(id2)
            p1 = db.getNameOfEntity(properties[0])
            p2 = db.getNameOfEntity(properties[1])
            tmpQuestionTemplate = question_template_compare.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY1]", prefix(cat) + " " + event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]",prefix(cat2) + " " +event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compareHelper[0])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(db.getNameOfEntity(curAnswer)) + ',' \
                                                                                                      ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([5],tmpQuestionTemplate,[db.getNameOfEntity(curAnswer)],[str(id),str(id2)],[str(curAnswer)],[str(properties[0]),str(properties[1])],None)

            tmpAnswer = id
            if curAnswer == id:
                tmpAnswer = id2
            tmpQuestionTemplate = question_template_compare.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY1]", prefix(cat) + " " +event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", prefix(cat2) + " " +event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compareHelper[1])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(
                db.getNameOfEntity(tmpAnswer)) + ',' \
                                                 ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([5],tmpQuestionTemplate,[db.getNameOfEntity(tmpAnswer)],[str(id),str(id2)],[str(tmpAnswer)],[str(properties[0]),str(properties[1])],None)



            tmpQuestionTemplate = question_template_compare_yn.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY1]", prefix(cat) + " " +event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", prefix(cat2) + " " +event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", 'has ' + compareHelper[0])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(curAnswer == id) + ',' \
                                                                                                         ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([5],tmpQuestionTemplate,[str(curAnswer == id)],[str(id),str(id2)],None,[str(properties[0]),str(properties[1])], None)


            tmpQuestionTemplate = question_template_compare.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY1]", prefix(cat) + " " +event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", prefix(cat2) + " " +event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", 'has ' + compareHelper[1])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(curAnswer != id) + ',' \
                                                                                                               ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([5],tmpQuestionTemplate,[str(curAnswer != id)],[str(id),str(id2)],None,[str(properties[0]),str(properties[1])],None)


print("}\n")
