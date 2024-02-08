import db
import requests
import json
import re
from question import Question
import time

#questionTemplateCountry = "In which country did the [ENTITY] happen?"
#questionTemplateCountryYesNo = "Did the [ENTITY] happen in [COUNTRY]?"
questionTemplateDate = "When [V1] the [ENTITY] [V2]?"
questionTemplateSignal = "Did [ENTITY1] [V] [SIGNAL] [ENTITY2]?"
questionTemplateFirst = "Did [ENTITY1] or [ENTITY2] [V] first?"
questionTemplateTripleFirst = "Which one [V] [ATTR] first, [ENTITY1], [ENTITY2] or [ENTITY3]?"
questionTemplateDoubleFirst = "Which one [V] [ATTR] first, [ENTITY1] or [ENTITY2]?"
questionAttributeInt = "[W] was [ATTR] of [ENTITY]?"
questionAttributePerson = "[W] was [ATTR] of [ENTITY]?"
questionAttributeCompDate = "Did the [ATTR] of [ENTITY1] happen [COMPARE] the [ATTR] of [ENTITY2]?"
questionAttributeComp = "Did the [ENTITY1] have a [COMPARE] [ATTR] than the [ENTITY2]?"
questionAttributeCompEv = "Did [ENTITY1] or [ENTITY2] have a [COMPARE] [ATTR]?"
questionAttributeTripleComp = "[ENTITY1], [ENTITY2] or [ENTITY3], which one had a [COMPARE] [ATTR]?"

# TODO ? in which entity was xy participant?
# TODO ? in how many entitys was xy participant?

def createBeforeAfterQuestion(entityid1, entity1,entity2id, entity2, signal, answer, verb):
    answerString = "no"
    if answer:
        answerString = "yes"
    tmpQuestionTemplate = questionTemplateSignal.replace("[ENTITY1]", entity1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", entity2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[V]", verb)
    print(tmpQuestionTemplate + answerString)
    #db.write_answer([4], tmpQuestionTemplate, [answerString], ['Q' + str(entityid1), 'Q' + str(entity2id)], None,None, None)


def createHappenFirstQuestion(entityid1, entity1,entity2id, entity2, isFirstEvent, verb):
    answer = entity2
    answerid = entity2
    if isFirstEvent:
        answer = entity1
        answerid = entity1
    tmpQuestionTemplate = questionTemplateFirst.replace("[ENTITY1]", entity1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", entity2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[V]", verb)
    print(tmpQuestionTemplate + answer)
    #db.write_answer([4], tmpQuestionTemplate, [answer], ['Q' + str(entityid1), 'Q' + str(entity2id)], ['Q' + str(answerid)],None, None)


print("[")


def createHappenFirstQuestionTriple(entityid1, entity1,entity2id, entity2, entity3, answerEvent, verb):
    tmpQuestionTemplate = questionTemplateTripleFirst.replace("[ENTITY1]", entity1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", entity2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY3]", entity3)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[V]", verb)
    return '{"question": "' + tmpQuestionTemplate + '",' \
                                                    ' "answer": "' + answerEvent + '",' \
                                                                                   ' "type": ' + json.dumps(
        4) + '},'


print("[")

def createAttributeQuestion(entityid, entity, attr, answer):
    tmpQuestionTemplate = questionAttributeInt.replace("[ENTITY]", entity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    print(tmpQuestionTemplate)
    print(answer)
    #db.write_answer([4], tmpQuestionTemplate, [answer], ['Q' + str(entityid)], None,None, None)

def createAttributePersonQuestion(entityid, entity, attr, answer):
    tmpQuestionTemplate = questionAttributePerson.replace("[ENTITY]", entity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    print(tmpQuestionTemplate + answer)
    #db.write_answer([4], tmpQuestionTemplate, [answer], ['Q' + str(entityid)], None,None, None)


print("[")

def createAttrCompQuestion(entityid1, entity1,entity2id, entity2, compr, attr, isFirstEvent):
    answer = "no"
    if isFirstEvent:
        answer = "yes"
    tmpQuestionTemplate = questionAttributeComp.replace("[ENTITY1]", entity1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", entity2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compr)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    print(tmpQuestionTemplate + answer)
    #db.write_answer([4], tmpQuestionTemplate, [answer], ['Q' + str(entityid1), 'Q' + str(entity2id)], None, None, None)



print("[")

def createAttrCompQuestionEv(entityid1, entity1,entity2id, entity2, compr, attr, isFirstEvent):
    answer = entity2
    answerid = entity2
    if isFirstEvent:
        answer = entity1
        answerid = entity1
    tmpQuestionTemplate = questionAttributeCompEv.replace("[ENTITY1]", entity1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", entity2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compr)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)

    print(tmpQuestionTemplate + answer)
    #db.write_answer([4], tmpQuestionTemplate, [answer], ['Q' + str(entityid1), 'Q' + str(entity2id)], ['Q' + str(answerid)], None, None)



print("[")


def createAttrCompQuestionTriple(entityid1, entity1,entity2id, entity2, entity3, answerEvent):
    tmpQuestionTemplate = questionAttributeTripleComp.replace("[ENTITY1]", entity1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTTIY2]", entity2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTTIY3]", entity3)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
    return '{"question": "' + tmpQuestionTemplate + '",' \
                                                    ' "answer": "' + answerEvent + '",' \
                                                                                   ' "type": ' + json.dumps(
        4) + '},'



print("[")

#isUnnamed = True

#if isUnnamed:
#    numberAttributes = db.read_db(
#        'SELECT e.qid, e.inception, e.publication_date, e.heritage_desg_date, e.birthday, e.floors, e.elevation, e.height, e.area, e.duration, e.cost, e.cost_currency, e.country, e.category,u."name"  FROM "entity_attributes_comp" e join "UnnamedEntity" u on e.qid = u.eventid ORDER BY qid ASC ')
#else:
#    numberAttributes =  db.read_db('SELECT * FROM "entity_attributes_comp" where qid > 1160004 ORDER BY qid ASC ')
numberAttributes =  db.read_db('SELECT * FROM "entity_attributes_comp" ORDER BY qid ASC ')
numberAttributes = [t + (False,) for t in numberAttributes]

unnumberAttributes = db.read_db(
        'SELECT e.qid, e.inception, e.publication_date, e.heritage_desg_date, e.birthday, e.floors, e.elevation, e.height, e.area, e.duration, e.cost, e.cost_currency, e.country, e.category,u."name"  FROM "entity_attributes_comp" e join "UnnamedEntity" u on e.qid = u.eventid ORDER BY qid ASC ')
unnumberAttributes = [t + (True,) for t in unnumberAttributes]

numberAttributes.extend(unnumberAttributes)
for qid, inception, publication_date, heritage_desg_date, birthday, floors, elevation, height, area, duration, cost, cost_currency, country, cat, entityName,isUnnamed in numberAttributes:
    #TODO
    #break
    print(qid)


    if cost_currency != '':
        try:
            currency = db.getNameOfEntity(cost_currency.rsplit("/",1)[1][1:])
            cost = cost + " " + currency
        except:
            cost = None

    inputCountry = None
    if country is not None:
        inputCountry = [country]

    attributes = [
        (inception, "the inception date",True),
        (publication_date, "the publication date", True),
        (heritage_desg_date, "the date of the heritage designation", True),
        (birthday, "the date of birth", True),
        (floors, "the number of floors above ground", False),
        (elevation, "the elevation above sea level",False),
        (height, "the height",False),
        (area, "the area",False),
        (duration, "the duration", False),
        (cost, "the cost",False)
    ]

    if (cat == ("movie" or "book")) and isUnnamed == False:
        entityName = "the " + cat + " " + entityName

    for attribute_value, attribute_name, isDate in attributes:
        if isDate:
            if attribute_value is not None:
                question = Question(False,(qid, entityName), [str(attribute_value),str(attribute_value)], [2], input_country=inputCountry, timeframe=[attribute_value,attribute_value])
                question.createQuestion(questionAttributeInt, attr=attribute_name,w="When")
        else:
            try:
                if attribute_value > -1:
                    if attribute_name == "the duration":
                        question = Question(False,(qid,str(entityName) + " in minutes"),[attribute_value],[2],input_country=inputCountry)
                        question.createQuestion(questionAttributeInt,attr=attribute_name, w="How long")
                    else:
                        question = Question(False,(qid,entityName),[attribute_value],[2],input_country=inputCountry)
                        question.createQuestion(questionAttributeInt,attr=attribute_name, w="What")
            except:
                print("error")

    entityPropertyList=[ ('P112', "the founder", "Who"),
    ('P136', "the genre", "What"),
    ('P495', "the country of origin", "What"),
    ('P57', "the director", "Who"),
    ('P58', "the screenwriter", "Who"),
    ('P86', "the composer", "Who"),
    ('P162', "the producer", "Who"),
    ('P840', "the narrative location", "Where"),
    ('P915', "the filming location", "Where"),
    ('P1435', "the heritage designation", "When"),
    ('P50', "the author", "Who"),
    ('P186', "the material made from", "What"),
    ('P84', "the architect", "Who"),
    ('P149', "the architectural style", "What"),
    ('P19', "the place of birth", "Where"),
    ('P22', "the father", "Who"),
    ('P25', "the mother", "Who")]



    for p,pLable,w in entityPropertyList:
        try:
            if db.entityHasProperty(qid,p):
                pResult = db.getAttributeOfEntities(qid,p)
                if pLable is not None:
                    try:
                        question = Question(False,(qid, entityName), db.getNameOfEnties(pResult), [2], input_country=inputCountry)
                        question.createQuestion(questionAttributePerson,attr=pLable,w=w)
                    except:
                        print("error")
        except:
            print("error")

    for qid2, inception2, publication_date2, heritage_desg_date2, birthday2, floors2, elevation2, height2, area2, duration2, cost2, cost_currency2, country2, cat2, entityName2,isUnnamed2 in numberAttributes:
        if cat == cat2:
            if qid != qid2:
                if True:

                    inputCountries2 = None
                    if not(country2 is None or country is None):
                        inputCountry2 = [country,country2]
                    inputCountry2 = None
                    if country2 is not None:
                        inputCountry2 = [country2]


                    if  (cat == ("movie" or "book")) and isUnnamed2 == False:
                        entityName2 = "the " + cat2 + " " + entityName2

                    attributes=[
                        (inception, inception2, "inception date",True),
                        (publication_date, publication_date2, "publication date",True),
                        (heritage_desg_date, heritage_desg_date2, "date of the heritage designation",True),
                        (birthday, birthday2, "date of birth",True),
                        (floors, floors2, "amount of floors above ground",False),
                        (elevation, elevation2, "elevation above sea level",False),
                        (height, height2, "height",False),
                        (area, area2, "area",False),
                        (duration, duration2, "duration",False),
                    ]

                    for attribute_value, attribute_value2, attribute_name, isDate in attributes:
                        try:
                            if isDate:
                                if attribute_value is not None and attribute_value2 is not None and attribute_value != attribute_value2:
                                    question = Question(False,(qid, entityName), [attribute_value < attribute_value2], [5,6], timeframe=[attribute_value,attribute_value2],
                                                        input_country=inputCountries2,entity2=(qid2, entityName2))

                                    question.createQuestion(questionAttributeCompDate, attr=attribute_name,compare="before")

                                    question.setAnswer([attribute_value > attribute_value2])
                                    question.createQuestion(questionAttributeCompDate, attr=attribute_name,compare="after")


                                    if attribute_value < attribute_value2:
                                        question.setAnswer([entityName])
                                        question.setAnswerEntity_id([qid])
                                        question.setOutput_country(inputCountry)
                                        question.createQuestion(questionTemplateDoubleFirst, attr=attribute_name,verb="had",spinnable=True)
                                    else:
                                        question.setAnswer([entityName2])
                                        question.setAnswerEntity_id([qid2])
                                        question.setOutput_country(inputCountry2)
                                        question.createQuestion(questionTemplateDoubleFirst, attr=attribute_name,verb="had",spinnable=True)


                            else:
                                if -1 < attribute_value != attribute_value2 > -1:
                                    question = Question(False,(qid, entityName),  [attribute_value > attribute_value2], [5],entity2=(qid2, entityName2), input_country=inputCountries2)
                                    question.createQuestion(questionAttributeComp, attr=attribute_name,compare="higher")

                                    question.setAnswer([attribute_value < attribute_value2])
                                    question.createQuestion(questionAttributeComp, attr=attribute_name,compare="lower")
                        except:
                            print("error")

#entitys = db.read_entitys()

exit(0)
##TODO
for id, name, start, end, point, cID, instancesIds, description, continent, pageviews in entitys:
    if description is not None:
        name = name + " " + description

    match = re.match(r'.*([1-2][0-9]{3})', name)
    if match is None:
        date = None
        if point is not None:
            date = [str(point), str(point)]
        elif end is not None:
            date = [str(start), str(end)]

        if date is not None:
            tmpQuestionTemplate = questionTemplateDate.replace("[ENTTIY]", name)
            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": "' + str(date) + '",' \
                                                                                              ' "type": ' + json.dumps(
                1) + '},'
        # print(json_data)

        for id2, name2, start2, end2, point2, cID2, instancesIds2, description2, continent2,pageviews2 in entitys:
            if description2 is not None:
                name2 = name2 + " " + description2
            if name2 is not name:
                match = re.match(r'.*([1-2][0-9]{3})', name2)
                if match is None:
                    # entity1 has point
                    if point is not None:
                        # entity2 has point
                        if point2 is not None:
                            print(createBeforeAfterQuestion(id, name, id2, name2, "before", point < point2))
                            print(createBeforeAfterQuestion(id, name, id2,  name2, "after", point > point2))
                            x = 1
                            if point != point2:
                                # print(createHappenFirstQuestion(name, name2, point < point2))
                                x = 1
                        # entity2 has start/end
                        elif end2 is not None:
                            if point != start2:
                                # print(createHappenFirstQuestion(name, name2, point < start2))
                                x = 1
                            if start2 > point or end2 < point:
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "before", point < start2))
                                print(createBeforeAfterQuestion(id, name, id2,  name2, "after", point > end2))
                                x = 1
                    # entity has start/end
                    elif end is not None:
                        # entity2 has point
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
