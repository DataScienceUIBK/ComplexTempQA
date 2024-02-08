#!/usr/bin/python
import SPARQL_reader
import json
import db
import pandas as pd


sparqlQuery = """SELECT ?item ?itemLabel ?date ?winner ?participants ?country WHERE {

  ?item wdt:P31/wdt:P279* wd:Q18536594.
  
  ?item wdt:P1346 ?winner.
  ?item wdt:P361 ?game.
  ?game wdt:P17 ?country.
  Optional {?item wdt:P1132 ?participants.}
  
  Optional { ?item wdt:P582 ?end.}
  Optional { ?item wdt:P585 ?date.}
  Optional { ?item wdt:P580 ?start.}
  
  { ?item wdt:P585 ?w585. BIND (?w585 as ?w)} UNION { ?item wdt:P580 ?w580. BIND (?w580 as ?w)
       }                                           
  FILTER ( YEAR(?w) >= 1987 )
  FILTER ( YEAR(?w) <= 2007)
  

    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }

}
ORDER BY ASC(?item)"""

questionTemplateCountry = "In which country happen the [EVENT]?"
questionTemplateCountryYesNo = "Was [COUNTRY] the location of the [EVENT]?"
questionAttributeWinner = "Who was the winner of [EVENT]?"
questionAttributePart = "What was the number of participants of [EVENT]?"
questionAttributeComp = "Did the [EVENT1] have a [COMPARE] number of participants than the [EVENT2]?"
questionAttributeCompEv = "Did [EVENT1] or [EVENT2] have a [COMPARE]  number of participants?"
questionAttributeTripleComp = "[EVENT1] or [EVENT2], which one had a [COMPARE] number of participants?"

def checkNextRow(idx, qid):
    wList = list()
    if idx+1 != len(queryResult):
        if queryResult.iat[idx+1,0] == qid:
            wList.append((db.getNameOfEntity(queryResult.iat[idx+1, 3][31:]),queryResult.iat[idx+1, 3][31:]))
            next = checkNextRow(idx+1, qid)
            if next is not None:
                wList += next
            return wList
    return None

def createAttrCompQuestionEv(event1, eventid1, event2,event2id, compr, isFirstEvent):
    answer = event2
    answerid = event2id
    if isFirstEvent:
        answer = event1
        answerid = eventid1
    tmpQuestionTemplate = questionAttributeCompEv.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compr)
    #return '{"question": "' + tmpQuestionTemplate + '",' \
    #                                                ' "answer": "' + answer + '",' \
    #                                                                          ' "type": ' + json.dumps(
    #    4) + '},'
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1),str(event2id)],
                    ['Q' + str(answerid)],
                    None, None)


def createAttrCompQuestion(event1, eventid1, event2,event2id, compr, answer):
    tmpQuestionTemplate = questionAttributeComp.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compr)
    #return '{"question": "' + tmpQuestionTemplate + '",' \
    #                                                ' "answer": "' + answer + '",' \
    #                                                                          ' "type": ' + json.dumps(
    #    4) + '},'
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1), str(event2id)],
                    None,
                    None, None)




def createAttrCompQuestionTriple(event1, event2, event3, compr, answerEvent):
    tmpQuestionTemplate = questionAttributeTripleComp.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT3]", event3)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compr)
    #return '{"question": "' + tmpQuestionTemplate + '",' \
    #                                                ' "answer": "' + answerEvent + '",' \
    #                                                                               ' "type": ' + json.dumps(
    #    4) + '},'
    db.write_answer([4], tmpQuestionTemplate, [answerEvent], [str(eventid1), str(event2id), str(event3id)],
                    ['Q' + str(answerid)],
                    None, None)




results_df = SPARQL_reader.readSPARQL(sparqlQuery, "")

queryResult = results_df[['item.value', 'itemLabel.value', 'date.value', 'winner.value', 'participants.value', 'country.value']]

skipRows = 0
partList = list()

for idx, row in queryResult.iterrows():
    if skipRows > 0:
        skipRows -= 1
        continue
    winnerList = list()
    qid = row['item.value']
    label = row['itemLabel.value']
    date = row['date.value']
    winnerList.append((db.getNameOfEntity(row['winner.value'][31:]),row['winner.value'][31:]))
    participants = row['participants.value']
    country = db.get_name_of_country(row['country.value'][32:])
    nextList = checkNextRow(idx,qid)
    if nextList is not None:
        winnerList += nextList
        winnerList = list(dict.fromkeys(winnerList))
        skipRows = len(winnerList)-1
    #print(winnerList)
    qid = qid[31:]
    tmpQuestionTemplate = questionTemplateCountry.replace("[EVENT]", label)
    json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                         ' "answer": "' + country + '",' \
                                                                                    ' "type": ' + json.dumps(
        1) + '},'
    #print(json_data)
    db.write_answer([1], tmpQuestionTemplate, [country],
                    [str(qid)],
                    [str(row['country.value'][32:])],
                    None, None)
    tmpQuestionTemplate = questionAttributeWinner.replace("[EVENT]", label)
    #json_data = '{"question": "' + tmpQuestionTemplate + '",' \
    #                                                     ' "answer": "' + str(winnerList[0]) + '",' \
    #                                                                                ' "type": ' + json.dumps(
    #    1) + '},'
    #print(json_data)
    #TODO answer id
    db.write_answer([1], tmpQuestionTemplate, [x[0] for x in winnerList],
                    [str(qid)],
                    [x[1] for x in winnerList],
                    None, None)
    tmpQuestionTemplate = questionAttributeWinner.replace("[EVENT]", label)

    # float means nan -> no value
    if type(participants) != float:
        tmpQuestionTemplate = questionAttributePart.replace("[EVENT]", label)
        json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                             ' "answer": "' + participants + '",' \
                                                                                           ' "type": ' + json.dumps(
            1) + '},'
        #print(json_data)
        # TODO answer id
        db.write_answer([1], tmpQuestionTemplate, [participants],
                        [str(qid)],
                        None,
                        None, None)

        partList.append((label,participants,qid))

for l,p,id in partList:
    for l2, p2,id2 in partList:
        if l != l2:
            createAttrCompQuestionEv(l,id, l2, id2, "higher", p > p2)
            createAttrCompQuestionEv(l,id, l2, id2, "lower", p < p2)
            answer = "no"
            if p > p2:
                answer = "yes"
            createAttrCompQuestion(l,id, l2, id2, "higher",answer)
            createAttrCompQuestion(l2,id2, l, id, "lower",answer)

            #--delete
            #answer = "no"
            #if p < p2:
            #    answer = "yes"
            #print(createAttrCompQuestion(l2, l, "higher",answer))
            #print(createAttrCompQuestion(l, l2, "lower",answer))
            #--delete end

            #for l3,p3 in partList:
            #    if l != l3 and l2 != l3:
            #        answer = l
            #        if p > p2 and p > p3:
            #            answer = l
            #        if p2 > p and l2 > p3:
            #            answer = l2
            #        if p3 > p and p3 > p2:
            #            answer = l3
            #        print(createAttrCompQuestionTriple(l, l2, l3, "higher", answer))
            #        if p < p2 and p < p3:
            #            answer = l
            #        if p2 < p and p2 < p3:
            #            answer = l2
            #        if p3 < p and p3 < p2:
            #            answer = l3
            #        print(createAttrCompQuestionTriple(l, l2, l3, "lower", answer))




