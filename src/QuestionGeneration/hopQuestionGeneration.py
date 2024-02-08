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

events = db.read_events()

question_template_time = "What was the [P2] of the [P1] where [EVENT] happen?"
question_template_unit = "What was the [P2] of the [P1] where [EVENT] happened in meter?"

question_template_compare_yn = "Comparing [P1], has [EVENT1] [COMPARE] [P2] than [EVENT2]?"
question_template_compare = "Comparing [P1] of [EVENT1] and [EVENT2], which one has a [COMPARE] [P2]?"


def extractQuestion(result, id, properties,description):
    answer = None
    if len(result[0]) <= 21:
        tmpQuestionTemplate = question_template_time.replace("[P1]", db.getNameOfEntity(properties[0]))
    else:
        tmpQuestionTemplate = question_template_unit.replace("[P1]", db.getNameOfEntity(properties[0]))
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", db.getNameOfEntity(properties[1]))
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT]", db.getNameOfEntity(id) + description)
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
        db.write_answer([1], tmpQuestionTemplate, [answer], ['Q' + str(id)],None,['P' + str(properties[0]),'P' + str(properties[1])], None)#['1987-01-01', '2007-12-31'])

    return id, answer, properties, description


def createSparqlAndQuestion(qid, properties, description):
    sparql = SPARQLGenerator2.SPARQLGenerator(qid, properties)
    results_df = SPARQL_reader.readSPARQL(sparql, "")
    if "var1.value" in results_df:
        return extractQuestion(results_df["var1.value"], qid, properties, description)
    return None


eventAnswer = list()


def appendIfNotNone(item):
    if item:
        eventAnswer.append(item)


print("{\n")

#try:
if True:
    for id, name, start, end, point, cID, instancesIds, description, continent, pageView in events:
        if description is not None:
            description = " " + description
        else:
            description = ""

        if description == " accident":
            properties = [["P137", "P571"], ["P121", "P606"], ["P121", "P2050"], ["P121", "P729"]]
        else:
            properties = [["P17", "P571"], ["P17", "P610"], ["P17", "P1589"], ["P276", "P571"], ["P276", "P610"],
                          ["P276", "P1589"]]

        for prop in properties:
            appendIfNotNone(createSparqlAndQuestion('Q' + str(id), prop, description))

#except:
#    x = 1

for id, answer, properties,description in eventAnswer:
    for id2, answer2, properties2, description2 in eventAnswer:
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

            event1 = db.getNameOfEntity(id) + description
            event2 = db.getNameOfEntity(id2) + description2
            p1 = db.getNameOfEntity(properties[0])
            p2 = db.getNameOfEntity(properties[1])
            tmpQuestionTemplate = question_template_compare.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT1]", event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]",event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compareHelper[0])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(db.getNameOfEntity(curAnswer)) + ',' \
                                                                                                      ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([4],tmpQuestionTemplate,[db.getNameOfEntity(curAnswer)],['Q' + str(id),'Q' + str(id2)],curAnswer,['P' + str(properties[0]),'P' + str(properties[1])])

            tmpAnswer = id
            if curAnswer == id:
                tmpAnswer = id2
            tmpQuestionTemplate = question_template_compare.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT1]", event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compareHelper[1])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(
                db.getNameOfEntity(tmpAnswer)) + ',' \
                                                 ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([4],tmpQuestionTemplate,[db.getNameOfEntity(tmpAnswer)],['Q' + str(id),'Q' + str(id2)],tmpAnswer,['P' + str(properties[0]),'P' + str(properties[1])])



            tmpQuestionTemplate = question_template_compare_yn.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT1]", event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", 'has ' + compareHelper[0])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(curAnswer == id) + ',' \
                                                                                                         ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([4],tmpQuestionTemplate,[str(curAnswer == id)],['Q' + str(id),'Q' + str(id2)],['P' + str(properties[0]),'P' + str(properties[1])])


            tmpQuestionTemplate = question_template_compare.replace("[P1]", p1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[P2]", p2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT1]", event1)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", 'has ' + compareHelper[1])

            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(curAnswer != id) + ',' \
                                                                                                               ' "type": ' + json.dumps(
                str(4)) + '},'
            #print(json_data)
            db.write_answer([4],tmpQuestionTemplate,[str(curAnswer != id)],['Q' + str(id),'Q' + str(id2)],['P' + str(properties[0]),'P' + str(properties[1])])


print("}\n")
