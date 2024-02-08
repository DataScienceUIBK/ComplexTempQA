import db
import requests
import json
import re
from datetime import datetime  # Add this import


questionTemplateCountry = "In which country did the [EVENT] happen?"
questionTemplateCountryYesNo = "Did the [EVENT] happen in [COUNTRY]?"
questionTemplateDate = "When was the [EVENT]?"
questionTemplateSignal = "Did [EVENT1] happen [SIGNAL] [EVENT2]?"
questionTemplateFirst = "Did [EVENT1] or [EVENT2] happen first?"
questionTemplateTripleFirst = "Which one happen first, [EVENT1], [EVENT2] or [EVENT3]?"
questionAttributeInt = "What was [ATTR] of [EVENT]?"
questionAttributePerson = "Who was [ATTR] of [EVENT]?"
questionAttributeComp = "Did the [EVENT1] have a [COMPARE] [ATTR] than the [EVENT2]?"
questionAttributeCompEv = "Did [EVENT1] or [EVENT2] have a [COMPARE] [ATTR]?"
questionAttributeTripleComp = "[EVENT1], [EVENT2] or [EVENT3], which one had a [COMPARE] [ATTR]?"

# TODO ? in which event was xy participant?
# TODO ? in how many events was xy participant?

def createBeforeAfterQuestion(eventid1, event1,event2id, event2, signal, answer):
    answerString = "no"
    if answer:
        answerString = "yes"
    tmpQuestionTemplate = questionTemplateSignal.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
    db.write_answer([4], tmpQuestionTemplate, [answerString], [str(eventid1), str(event2id)], None,
                    None, None)


def createHappenFirstQuestion(eventid1, event1,event2id, event2, isFirstEvent):
    answer = event2
    answerid = event2
    if isFirstEvent:
        answer = event1
        answerid = event1
    tmpQuestionTemplate = questionTemplateFirst.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1), str(event2id)], [str(answerid)],
                    None, None)


print("[")


def createHappenFirstQuestionTriple(eventid1, event1,event2id, event2, event3, answerEvent):
    tmpQuestionTemplate = questionTemplateTripleFirst.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT3]", event3)
    return '{"question": "' + tmpQuestionTemplate + '",' \
                                                    ' "answer": "' + answerEvent + '",' \
                                                                                   ' "type": ' + json.dumps(
        4) + '},'


print("[")

def createAttributeQuestion(eventid, event, attr, answer):
    tmpQuestionTemplate = questionAttributeInt.replace("[EVENT]", event)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid)], None,
                    None, None)

def createAttributePersonQuestion(eventid, event, attr, answer,answerid):
    tmpQuestionTemplate = questionAttributePerson.replace("[EVENT]", event)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    db.write_answer([4], tmpQuestionTemplate, answer, [str(eventid)], answerid,
                    None, None)


print("[")

def createAttrCompQuestion(eventid1, event1,event2id, event2, compr, attr, isFirstEvent):
    answer = "no"
    if isFirstEvent:
        answer = "yes"
    tmpQuestionTemplate = questionAttributeComp.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compr)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1), str(event2id)], None, None, None)



print("[")

def createAttrCompQuestionEv(eventid1, event1,event2id, event2, compr, attr, isFirstEvent):
    answer = event2
    answerid = event2id
    if isFirstEvent:
        answer = event1
        answerid = eventid1
    tmpQuestionTemplate = questionAttributeCompEv.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compr)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)

    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1), str(event2id)], [ str(answerid)], None, None)



print("[")


def createAttrCompQuestionTriple(eventid1, event1,event2id, event2, event3, answerEvent):
    tmpQuestionTemplate = questionAttributeTripleComp.replace("[EVENT1]", event1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT2]", event2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[EVENT3]", event3)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    return '{"question": "' + tmpQuestionTemplate + '",' \
                                                    ' "answer": "' + answerEvent + '",' \
                                                                                   ' "type": ' + json.dumps(
        4) + '},'



print("[")

numberAttributes = db.readAttributeEvents()

if False:
#for eventId, deaths, injured, survior, participants, wind, pressure, ballots, voters, attendance, valid_votes, magnitude, depth, matches_start, points_score, perpetrators, neg_votes, support_votes in numberAttributes:
    #TODO
    #break
    event = db.read_event(eventId)
    #if len(event) == 0:
        #continue
    eventName = event[0][0]
    if event[0][1] is not None:
        eventName = eventName + " " + event[0][1]
    attributes = [
        (deaths, "the number of death"),
        (injured, "the number of injured people"),
        (survior, "the number of survivors"),
        (participants, "the number of participants"),
        (wind, "maximum sustained wind in m/s"),
        (pressure, "lowest atmospheric pressure in hectopascal"),
        (ballots, "total number of ballot(s) cast"),
        (voters, "number of eligible voters"),
        (attendance, "number of attendance"),
        (valid_votes, "number of valid votes"),
        (magnitude, "earthquake magnitude on the Richter magnitude scale"),
        (depth, "vertical depth"),
        (matches_start, "number of games played"),
        (points_score, "number of points scored"),
        (perpetrators, "number of perpetrators"),
        (neg_votes, "number of negative votes"),
        (support_votes, "number of support votes")
    ]

    for attribute_value, attribute_name in attributes:
        if attribute_value > -1:
            if not eventName.__contains__(attribute_name.split(" ")[-1]):
                createAttributeQuestion(eventId, eventName, attribute_name, attribute_value)

    entityPropertyList=[('P710',"the participant",True),
                        ('P1427',"the start point",False), #what is
                        ('P1444',"the destination point",False), #what is
                        ('P726',"the candidate",True),
                        ('P1346',"the winner",True),
                        ('P533',"the target",True),
                        ('P664',"the organizer",True),
                        ('P121',"the item operated",False), #what is
                        ('P520',"the armament",False), #what is
                        ('P371',"presenter",True),
                        ('P8031',"perpetrator",True)]

    for p,pLable,isPerson in entityPropertyList:
        if not eventName.__contains__(attribute_name.split(" ")[-1]):
            if db.entityHasProperty(eventId,p):
                pResultid = db.getAttributeOfEntities(eventId,p)
                pResult = db.getNameOfEnties(pResultid)
                if pLable is not None:
                    if isPerson:
                        createAttributePersonQuestion(eventId, eventName, pLable, pResult,pResultid)
                    else:
                        createAttributeQuestion(eventId, eventName, pLable, pResult)

    for eventId2, deaths2, injured2, survior2, participants2, wind2, pressure2, ballots2, voters2, attendance2, valid_votes2, magnitude2, depth2, matches_start2, points_score2, perpetrators2, neg_votes2, support_votes2 in numberAttributes:
        if eventId != eventId2:

            event2 = db.read_event(eventId2)
            if len(event2) == 0:
                continue
            eventName2 = event2[0][0]
            if event2[0][1] is not None:
                eventName2 = eventName2 + " " + event2[0][1]

            attributes = [
                (deaths, deaths2, "the number of death"),
                (injured, injured2, "the number of injured people"),
                (survior, survior2, "the number of survivors"),
                (participants, participants2, "the number of participants"),
                (wind, wind2, "maximum sustained wind in m/s"),
                (pressure, pressure2, "lowest atmospheric pressure in hectopascal"),
                (ballots, ballots2, "total number of ballot(s) cast"),
                (voters, voters2, "number of eligible voters"),
                (attendance, attendance2, "number of attendance"),
                (valid_votes, valid_votes2, "number of valid votes"),
                (magnitude, magnitude2, "earthquake magnitude on the Richter magnitude scale"),
                (depth, depth2, "vertical depth"),
                (matches_start, matches_start2, "number of games played"),
                (points_score, points_score2, "number of points scored"),
                (perpetrators, perpetrators2, "number of perpetrators"),
                (neg_votes, neg_votes2, "number of negative votes"),
                (support_votes, support_votes2, "number of support votes")
            ]

            for attribute_value, attribute_value2, attribute_name in attributes:
                if not eventName.__contains__(attribute_name.split(" ")[-1]) or eventName2.__contains__(attribute_name.split(" ")[-1]) :
                    if -1 < attribute_value != attribute_value2 > -1:
                        createAttrCompQuestion(eventId, eventName, eventId2, eventName2, "higher", attribute_name,
                                                     attribute_value > attribute_value2)
                        createAttrCompQuestion(eventId, eventName, eventId2, eventName2, "lower", attribute_name,
                                                     attribute_value < attribute_value2)
                        createAttrCompQuestionEv(eventId, eventName, eventId2, eventName2, "higher", attribute_name,
                                                       attribute_value > attribute_value2)

events = db.read_events()

for id, name, start, end, point, cID, instancesIds, description, continent, pageviews in events:
    if description is not None:
        name = name + " " + description
    if cID is not None:
        link = 'https://www.wikidata.org/wiki/Special:EntityData/' + cID + '.json'
        dataJson = requests.get(link).json().get('entities').get(cID)
        if "P17" in dataJson["claims"]:
            part = dataJson["claims"]["P17"][0]["mainsnak"]
            if "datavalue" in part:
                countryId = part["datavalue"]["value"]["id"]
                country = db.get_name_of_country(countryId)
                if not (name.__contains__(country)):
                    tmpQuestionTemplate = questionTemplateCountry.replace("[EVENT]", name)
                    json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                         ' "answer": "' + country + '",' \
                                                                                                    ' "type": ' + json.dumps(
                        1) + '},'
                    #print(json_data)
                    #db.write_answer([1], tmpQuestionTemplate, [country], [str(id)],[countryId],None, None)
                    countries = db.read_countries()
                    for otherCountryId in countries:
                        otherCountry = db.get_name_of_country(otherCountryId[0])
                        continent2 = db.getAttributeOfEntities(otherCountryId[0],'P30')[0]#TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if otherCountry is not None:

                            if continent is not None and continent2 is not None and continent == continent2:
                                answer = "No"
                                if otherCountry == country:
                                    answer = "Yes"
                                tmpQuestionTemplate = questionTemplateCountryYesNo.replace("[EVENT]", name)
                                tmpQuestionTemplate = tmpQuestionTemplate.replace("[COUNTRY]", otherCountry)
                                json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                                     ' "answer": "' + answer + '",' \
                                                                                                                ' "type": ' + json.dumps(
                                    1) + '},'
                                #print(json_data)
                                #db.write_answer([1], tmpQuestionTemplate, [answer], [str(id), countryId], None, None, None)

    #link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(id) + '.json'
    #dataJson = requests.get(link).json().get('entities').get('Q' + str(id))
    #if "P1120" in dataJson["claims"]:
    #    part = dataJson["claims"]["P1120"][0]["mainsnak"]
    #    if "datavalue" in part:
    #        result = part["datavalue"]["value"]["amount"]
    #        if result.__contains__("+"):
    #            result = int(result.replace("+", ""))
    #        tmpQuestionTemplate = questionAttributeInt.replace("[EVENT]", name)
    #        tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", "number of deaths")  # TODO
    #        json_data = '{"question": "' + tmpQuestionTemplate + '",' \
    #                                                             ' "answer": "' + str(result) + '",' \
    #                                                                                            ' "type": ' + json.dumps(
    #            1) + '},'
    #        print(json_data)

    match = re.match(r'.*([1-2][0-9]{3})', name)
    print(name)
    print(match)
    if match is None:
        print("here")
        date = None
        if point is not None:
            date = [str(point), str(point)]
        elif end is not None:
            date = [str(start), str(end)]
        print(date)
        if date is not None:
            tmpQuestionTemplate = questionTemplateDate.replace("[EVENT]", name)
            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": "' + str(date) + '",' \
                                                                                              ' "type": ' + json.dumps(
                [1,3]) + '},'
            db.write_answer([1,3], tmpQuestionTemplate, date, [str(id)], None,
                            None, [datetime.strptime(str(date[0]), '%Y-%m-%d').date(), datetime.strptime(str(date[1]), '%Y-%m-%d').date()])
        # print(json_data)

        for id2, name2, start2, end2, point2, cID2, instancesIds2, description2, continent2,pageviews2 in events:
            if description2 is not None:
                name2 = name2 + " " + description2
            if name2 is not name:
                match = re.match(r'.*([1-2][0-9]{3})', name2)
                if match is None:
                    # event1 has point
                    if point is not None:
                        # event2 has point
                        if point2 is not None:
                            print(createBeforeAfterQuestion(id, name, id2, name2, "before", point < point2))
                            print(createBeforeAfterQuestion(id, name, id2,  name2, "after", point > point2))
                            x = 1
                            if point != point2:
                                # print(createHappenFirstQuestion(name, name2, point < point2))
                                x = 1
                        # event2 has start/end
                        elif end2 is not None:
                            if point != start2:
                                # print(createHappenFirstQuestion(name, name2, point < start2))
                                x = 1
                            if start2 > point or end2 < point:
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "before", point < start2))
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "after", point > end2))
                                x = 1
                    # event has start/end
                    elif end is not None:
                        # event2 has point
                        if point2 is not None:
                            if point2 != start:
                                # print(createHappenFirstQuestion(name, name2, start < point2))
                                x = 1
                            if start > point2 or end < point2:
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "before", start < point2))
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "after", end > point2))
                                x = 1
                        elif end2 is not None:
                            if start != start2:
                                # print(createHappenFirstQuestion(name, name2, start < start2))
                                x = 1
                            if (start < start2 and end < end2) or (start > start2 and end > end2):
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "before", start < start2))
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "after", end > end2))





print("]")
