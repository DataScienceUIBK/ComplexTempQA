import pandas as pd
import sys
import requests
import db
import SPARQL_reader
import json
import datetime
import time
from collections import Counter
import nltk  # $ pip install nltk
from nltk.corpus import cmudict  # >>> nltk.download('cmudict')
from datetime import datetime  # Add this import


input_sparql_result = db.read_spraql_input()

#print("[")

def starts_with_vowel_sound(word, pronunciations=cmudict.dict()):
    for syllables in pronunciations.get(word, []):
        return syllables[0][-1].isdigit()  # use only the first one


def getAttributeByEntitiy(eventId, property):
    link = 'https://www.wikidata.org/wiki/Special:EntityData/' + eventId + '.json'
    dataJson = requests.get(link).json().get('entities').get(eventId)
    countryList = []
    if property in dataJson["claims"]:
        for c in dataJson["claims"][property]:
            countryList.append(c["mainsnak"]["datavalue"]["value"]["id"])
    return countryList


def getCountryByEntitiy(eventId):
    link = 'https://www.wikidata.org/wiki/Special:EntityData/' + eventId + '.json'
    dataJson = requests.get(link).json().get('entities').get(eventId)
    countryList = []
    if "P17" in dataJson["claims"]:
        for c in dataJson["claims"]["P17"]:
            if not( "qualifiers" in c and "P582" in c["qualifiers"]):
                if "datavalue" in c["mainsnak"]:
                    countryList.append(c["mainsnak"]["datavalue"]["value"]["id"])
    elif "P276" in dataJson["claims"]:
        for c in dataJson["claims"]["P276"]:
            if not ("qualifiers" in c and "P582" in c["qualifiers"]):
                if "datavalue" in c["mainsnak"]:
                    countryList.extend(getCountryByEntitiy(c["mainsnak"]["datavalue"]["value"]["id"]))

    return countryList


def toDate(rawDate):
    if rawDate is None:
        return None
    else:
        return datetime.date.fromisoformat(rawDate)


t = None

def idsListToString(qids):
    result = []
    for q in qids:
        result.append(db.getNameOfEntity(q))
    return result


def countQuestionEntityEvent(entityDates, eventName, prefix):
    print(entityDates)
    for entitiy in entityDates:
        tmpName = db.getNameOfEntity(entitiy)
        if tmpName is None:
            continue
        entityName = prefix + tmpName

        counts = Counter(entityDates[entitiy])


        tmpQuestionTemplate = question_template.replace("[EVENT]", eventName)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[TIME]",
                                                          "between 1987 and 2007 " + entityName)
        json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                             ' "answer": ' + json.dumps(
            len(entityDates[entitiy])) + ',' \
                                     ' "type": ' + json.dumps(type) + '},'
        print("a" + json_data)
        db.write_answer(type, tmpQuestionTemplate, [len(entityDates[entitiy])], [entitiy],None, None, [datetime.strptime('1987-01-01', '%Y-%m-%d').date(), datetime.strptime('2007-12-31', '%Y-%m-%d').date()])

        tmpQuestionTemplate = tmpQuestionTemplate.replace("How often","In how many years")
        db.write_answer(type + [9], tmpQuestionTemplate, [len(entityDates[entitiy])], [entitiy],None, None, [datetime.strptime('1987-01-01', '%Y-%m-%d').date(), datetime.strptime('2007-12-31', '%Y-%m-%d').date()])




        for key in counts:
            tmpQuestionTemplate = question_template.replace("[EVENT]", eventName)
            tmpQuestionTemplate = tmpQuestionTemplate.replace("[TIME]",
                                                              entityName + " in " + str(key))
            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                 ' "answer": ' + json.dumps(
                counts[key]) + ',' \
                         ' "type": ' + json.dumps(type) + '},'
            print(json_data)
            db.write_answer(type, tmpQuestionTemplate,  [counts[key]], [entity], None, None,[datetime.strptime(str(key) + '-01-01', '%Y-%m-%d').date(), datetime.strptime(str(key) + '-12-31', '%Y-%m-%d').date()])


for prefix, entity, id_input, descr, pageView, input_id, sparql_id, id_sparql, template, desc_sparql in input_sparql_result:

    input_string = "wd:" + prefix + str(entity)
    results_df = SPARQL_reader.readSPARQL(template, input_string)
    queryResult = None
    if 'start.value' and 'end.value' and 'date.value' in results_df:
        queryResult = results_df  # [['itemLabel.value', 'start.value', 'end.value','date.value']]
    elif 'start.value' and 'end.value' in results_df:
        queryResult = results_df[['item.value', 'start.value', 'end.value']]
    elif 'date.value' in results_df:
        queryResult = results_df[['item.value', 'date.value']]

    outputEntityId = input_string.split(':')[1]
    outputEntity = db.getNameOfEntity(outputEntityId)
    print(outputEntity)


    link = 'https://www.wikidata.org/wiki/Special:EntityData/' + input_string.split(':')[1] + '.json'
    dataJson = requests.get(link).json().get('entities').get(input_string.split(':')[1])
    country = None
    countryId = None
    continentId = None
    if "P17" in dataJson["claims"]:
        countryId = dataJson["claims"]["P17"][0]["mainsnak"]["datavalue"]["value"]["id"]
        country = db.get_name_of_country(countryId)
        link = 'https://www.wikidata.org/wiki/Special:EntityData/' + str(countryId) + '.json'
        dataJson = requests.get(link).json().get('entities').get(str(countryId))
        if "P30" in dataJson["claims"]:
            continentId = dataJson["claims"]["P30"][0]["mainsnak"]["datavalue"]["value"]["id"]

    question_template_result = db.read_template_question_by_input(id_input)

    for id_question_template, question_template, type, method, a, b, c, d, e, f,p in question_template_result:
        # 1 count year
        # 2 aggreage
        # 3 before after
        # 4 time question
        if queryResult is None:
            continue
        if method != 1 and method != 2:
            continue
        print(method)
        if method == 1:
            print("here")
            timeQuestion = list()
            eventQuestion = dict()
            if True:
                i=1987
            #for i in range(1987, 2008):
                result = []
                for idx, row in queryResult.iterrows():
                    if 'start.value' and 'end.value' in results_df:
                        startYear = int(row['start.value'][:4])
                        endYear = int(row['end.value'][:4])

                        print("start")
                        print(row['start.value'][:10])
                        print(row['end.value'][:10])
                        print(outputEntity)
                        print(outputEntityId)
                        if countryId is not None:
                            c = countryId[1:]
                        else:
                            c = None
                        print(row['item.value'].rsplit('/', 1)[1][1:])
                        print("end")
                        query = f'INSERT INTO "Entities" ("EntityID", "Name", "StartDate", "category", "Country", "EndDate") VALUES (' \
                                + str(row['item.value'].rsplit('/', 1)[1][1:]) + ",'" + str(db.getNameOfEntity(row['item.value'].rsplit('/', 1)[1])) + \
                                "','" + str(row['start.value'][:10])  + "', 'person' ," + str(c) + ",'" + str(row['end.value'][:10]) + "')"

                        print(query)

                        # Assuming you have a function called db.write_db to execute the query
                        #db.write_db(query)

                        if startYear <= i <= endYear:
                            result.append((row['item.value'].rsplit('/', 1)[1]))
                            eventQuestion.update(
                                {row['item.value'].rsplit('/', 1)[1]: (row['start.value'][:10], row['end.value'][:10])})
                    elif 'date.value' in results_df:
                        date = int(row['date.value'][:4])

                        print("start")
                        print(row['date.value'][:10])
                        print(outputEntity)
                        print(outputEntityId)
                        if countryId is not None:
                            c = countryId[1:]
                        else:
                            c = None
                        print(row['item.value'].rsplit('/', 1)[1][1:])
                        print("end")

                        query = f'INSERT INTO "Entities" ("EntityID", "Name", "StartDate", "category", "Country", "EndDate") VALUES (' \
                                + str(row['item.value'].rsplit('/', 1)[1][1:]) + ",'" + str(db.getNameOfEntity(row['item.value'].rsplit('/', 1)[1])) + \
                                "','" + str(row['date.value'][:10])  + "', 'person' ," + str(c) + ",NULL)"

                        print(query)

                        # Assuming you have a function called db.write_db to execute the query
                        #db.write_db(query)



                        if i == date:
                            result.append(row['item.value'].rsplit('/', 1)[1])
                        eventQuestion.update({row['item.value'].rsplit('/', 1)[1]: (row['date.value'][:10], None)})
                timeQuestion.append((i, result))

            for year, person in timeQuestion:
                tmpQuestionTemplate = question_template.replace("[ENTITY]", outputEntity)
                tmpQuestionTemplate = tmpQuestionTemplate.replace("[YEAR]", "in " + str(year))
                #json_data = '{"question": "' + tmpQuestionTemplate[:-1] + '",' \
                #                                                          ' "answer": ' + json.dumps(db.getNameOfEntity(person)) + ',' \
                #                                                                                               ' "type": ' + json.dumps(
                #    type) + '},'
                #print(json_data)
                if len(person) > 0:
                    db.write_answer(type, tmpQuestionTemplate, idsListToString(person), [outputEntityId], person, None,[datetime.strptime(str(year) + '-01-01', '%Y-%m-%d').date(), datetime.strptime(str(year) +'-12-31', '%Y-%m-%d').date()])
            if countryId is not None:
                events = db.read_event_by_country(countryId, continentId)
                if len(events) > 0:
                    for id, name, start, end, point, cID, instancesIds, description, continent, views in events:
                        if description is not None:
                            name = name + " " + description
                        result = []
                        for person in eventQuestion:
                            personStart = toDate(eventQuestion[person][0])
                            personEnd = toDate(eventQuestion[person][1])
                            dates = None

                            # event has point in time
                            if start is None:
                                # person has point in time
                                if personEnd is None:
                                    if point == personStart:
                                        result.append(person)
                                elif personStart <= point <= personEnd:
                                    result.append(person)
                                dates=[point,point]
                            else:
                                if end is None:
                                    continue

                                if personEnd is None:
                                    if start <= personStart <= end:
                                        result.append(person)
                                elif start <= personStart and personEnd <= end:
                                    result.append(person)
                                dates=[start,end]

                        if len(result) > 0:
                            tmpQuestionTemplate = question_template.replace("[ENTITY]", outputEntity)
                            tmpQuestionTemplate = tmpQuestionTemplate.replace("[YEAR]", "during the " + name)
                            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                                 ' "answer": ' + json.dumps(
                                result) + ',' \
                                          '"type": ' + json.dumps(
                                type) + '},'
                            #print(json_data)
                            db.write_answer(type, tmpQuestionTemplate, idsListToString(result), [outputEntityId],
                                            result, None,[datetime.strptime(str(dates[0]) + '-01-01', '%Y-%m-%d').date(), datetime.strptime(str(dates[1]) + '-12-31', '%Y-%m-%d').date()])

        elif method == 2:
            resultQuestion = dict()
            for idx, row in queryResult.iterrows():
                item = row['item.value'].rsplit('/', 1)[1]
                count = 1
                if item in resultQuestion:
                    count = resultQuestion[item]
                    count += 1
                resultQuestion.update({item: count})
            for key in resultQuestion:
                tmpQuestionTemplate = question_template.replace("[ENTITY]", outputEntity)
                tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", db.getNameOfEntity(key))
                # print(tmpQuestionTemplate[:-1])
                # print(resultQuestion[key])
                json_data = '{"question": "' + tmpQuestionTemplate[:-1] + '",' \
                                                                          ' "answer": ' + json.dumps(
                    resultQuestion[key]) + ',' \
                                           ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type, tmpQuestionTemplate, [resultQuestion[key]], [outputEntityId, key],
                                None, None, [datetime.strptime('1987-01-01', '%Y-%m-%d').date(), datetime.strptime('2007-12-31', '%Y-%m-%d').date()])
        elif method == 3:
            signalQuestionTemplate = "Was [ENTITY1] [ACTION] [SIGNAL] [ENTITY2]?"
            doubleQuestionTemplate = "Who was first [ACTION], [ENTITY1] or [ENTITY2]?"
            tripleQuestionTemplate = "Was [ENTITY1], [ENTITY2] or [ENTITY3] [ACTION] first?"
            beforeQuestion = list()
            afterQuestion = list()
            tripleQuestion = list()

            before = None
            for idx, row in queryResult.iterrows():
                item = row['item.value'].rsplit('/', 1)[1]
                if before is not None:
                    beforeQuestion.append((item, before))
                    afterQuestion.append((before, item))
                    if len(afterQuestion) > 1:
                        tripleQuestion.append((afterQuestion[len(afterQuestion)-2][0],before,item))
                before = item
            signal = "before"
            for beforeTuple in beforeQuestion:
                tmpQuestionTemplate = question_template.replace("[ENTITY]", outputEntity)
                tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", db.getNameOfEntity(beforeTuple[0]))
                tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
                # print(tmpQuestionTemplate[:-1])
                # print(beforeTuple[1])
                json_data = '{"question": "' + tmpQuestionTemplate[:-1] + '",' \
                                                                          ' "answer": ' + json.dumps(
                    beforeTuple[1]) + ',' \
                                      ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type,tmpQuestionTemplate, [db.getNameOfEntity(beforeTuple[1])], [outputEntityId, beforeTuple[0]], [beforeTuple[1]], None, None)

                tmpSignalQuestionTemplate = signalQuestionTemplate.replace("[ENTITY1]", db.getNameOfEntity(beforeTuple[0]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ENTITY2]", db.getNameOfEntity(beforeTuple[1]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ACTION]", outputEntity)
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[SIGNAL]", signal)
                json_data = '{"question": "' + tmpSignalQuestionTemplate + '",' \
                                                                          ' "answer": ' + json.dumps(
                    "No") + ',' \
                                      ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type,tmpSignalQuestionTemplate, ["No"], [beforeTuple[0],beforeTuple[1],outputEntityId], None, None, None)

                tmpSignalQuestionTemplate = doubleQuestionTemplate.replace("[ENTITY1]", db.getNameOfEntity(beforeTuple[1]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ENTITY2]", db.getNameOfEntity(beforeTuple[0]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ACTION]", outputEntity)
                json_data = '{"question": "' + tmpSignalQuestionTemplate + '",' \
                                                                           ' "answer": ' + json.dumps(
                    beforeTuple[1]) + ',' \
                             ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type,tmpSignalQuestionTemplate, [db.getNameOfEntity(beforeTuple[1])], [outputEntityId, beforeTuple[0]], [beforeTuple[1]], None,None)

            signal = "after"
            for afterTuple in afterQuestion:
                tmpQuestionTemplate = question_template.replace("[ENTITY]", outputEntity)
                tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", db.getNameOfEntity(afterTuple[0]))
                tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
                # print(tmpQuestionTemplate[:-1])
                # print(afterTuple[1])
                json_data = '{"question": "' + tmpQuestionTemplate[:-1] + '",' \
                                                                          ' "answer": ' + json.dumps(
                    afterTuple[1]) + ',' \
                                     ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type,tmpQuestionTemplate, [db.getNameOfEntity(afterTuple[1])], [outputEntityId, afterTuple[0]], [afterTuple[1]], None,None)

                tmpSignalQuestionTemplate = signalQuestionTemplate.replace("[ENTITY1]", db.getNameOfEntity(afterTuple[0]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ENTITY2]", db.getNameOfEntity(afterTuple[1]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ACTION]", outputEntity)
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[SIGNAL]", signal)
                json_data = '{"question": "' + tmpSignalQuestionTemplate + '",' \
                                                                           ' "answer": ' + json.dumps(
                    "No") + ',' \
                            ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type,tmpSignalQuestionTemplate, ["No"], [afterTuple[0],afterTuple[1],outputEntityId], None, None,None)

                tmpSignalQuestionTemplate = signalQuestionTemplate.replace("[ENTITY1]", db.getNameOfEntity(afterTuple[1]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ENTITY2]", db.getNameOfEntity(afterTuple[0]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ACTION]", outputEntity)
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[SIGNAL]", signal)
                json_data = '{"question": "' + tmpSignalQuestionTemplate + '",' \
                                                                           ' "answer": ' + json.dumps(
                    "Yes") + ',' \
                             ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type,tmpSignalQuestionTemplate, ['Yes'], [outputEntityId,afterTuple[1], afterTuple[0]],None, None,None)

            for triple in tripleQuestion:
                tmpSignalQuestionTemplate = tripleQuestionTemplate.replace("[ENTITY1]", db.getNameOfEntity(triple[0]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ENTITY2]", db.getNameOfEntity(triple[1]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ENTITY3]", db.getNameOfEntity(triple[2]))
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[ACTION]", outputEntity)
                tmpSignalQuestionTemplate = tmpSignalQuestionTemplate.replace("[SIGNAL]", signal)
                json_data = '{"question": "' + tmpSignalQuestionTemplate + '",' \
                                                                           ' "answer": ' + json.dumps(
                    triple[0]) + ',' \
                            ' "type": ' + json.dumps(type) + '},'
                #print(json_data)
                db.write_answer(type,tmpSignalQuestionTemplate, [db.getNameOfEntity(triple[0])], [triple[0], triple[1], triple[2]], [triple[0]], None,None)


        elif method == 4:
            resultQuestion = dict()
            for idx, row in queryResult.iterrows():
                date = ""
                item = row['item.value'].rsplit('/', 1)[1]
                if 'start.value' and 'end.value' in results_df:
                    startYear = row['start.value'][:10]
                    endYear = row['end.value'][:10]
                    date = [str(startYear),str(endYear)]
                elif 'date.value' in results_df:
                    date = [row['date.value'][:10],row['date.value'][:10]]
                dateList = list()
                if item in resultQuestion:
                    dateList = resultQuestion[item]
                dateList.append(date)
                resultQuestion.update({item: dateList})

            for key in resultQuestion:
                tmpQuestionTemplate = question_template.replace("[ENTITY]", outputEntity)
                tmpQuestionTemplate = tmpQuestionTemplate.replace("[PERSON]", db.getNameOfEntity(key))
                # print(tmpQuestionTemplate[:-1])
                # print(resultQuestion[key])
                json_data = '{"question": "' + tmpQuestionTemplate[:-1] + '",' \
                                                                          ' "answer": ' + json.dumps(
                    resultQuestion[key]) + ',' \
                                           ' "type": ' + json.dumps(type) + '},'
                print(json_data)
                print(key)
                print(outputEntityId)
                print(resultQuestion[key])
                print(resultQuestion[key][0])
                print(resultQuestion[key][0][0])
                db.write_answer(type, tmpQuestionTemplate, resultQuestion[key][0], [key], None, None,[datetime.strptime(str(resultQuestion[key][0][0]), '%Y-%m-%d').date(), datetime.strptime(str(resultQuestion[key][0][1]), '%Y-%m-%d').date()])


        elif method == 5:
            print("here")
            attributes = {
                "P1120": (" with more than [number] deaths", 0),
                "P1339": (" with more than [number] injured people", 0),
                "P1561": (" with more than [number] survivors", 0),
                "P1132": (" with more than [number] participants", 0),
                "P1868": (" with more than [number] ballot(s) cast", 0),
                "P1867": (" with more than [number] eligible voters", 0),
                "P1110": (" with more than [number] spectators", 0),
                "P1697": (" with more than [number] total valid votes", 0),
                "P2528": ( "with more than [number] magnitude on the Richter magnitude scale", 0),
                "P1350": (" with more than [number] games played", 0),
                "P1351": (" with more than [number] points scored", 0),
                "P3886": (" with more than [number] perpetrators", 0),
                "P8682": (" with more than [number] negative votes", 0),
                "P8683": (" with more than [number] support votes", 0)
            }

            for p, value in attributes.items():
                sparqlQuery = """
                SELECT (AVG(?attr) AS ?average)
                        WHERE {
                          SELECT DISTINCT ?item ?attr
                          WHERE {
                            ?item wdt:P31/wdt:P279* wd:Q744913.
                            ?item wdt:[ATTR] ?attr.
                            OPTIONAL { ?item wdt:P582 ?end. }
                            OPTIONAL { ?item wdt:P585 ?date. }
                            OPTIONAL { ?item wdt:P580 ?start. }
                            { ?item wdt:P585 ?w585. BIND(?w585 AS ?w) }
                            UNION
                            { ?item wdt:P580 ?w580. BIND(?w580 AS ?w) }
                            FILTER(YEAR(?w) >= 1987 && YEAR(?w) <= 2007)
                          }
                        }
                """
                sparqlQuery = sparqlQuery.replace("[ATTR]",p)
                average = int(float(SPARQL_reader.readSPARQL(sparqlQuery,"")["average.value"][0]))

                if average > 0:
                    attributes[p] = (value[0].replace("[number]",str(average)),average)
                    #TODO vielleicht mehere einträge mit +- 1 average


            yearCount = dict()
            countryDates = dict()
            operatorDates = dict()
            total = 0
            for p, value in attributes.items():
                if value[1] > 0:

                    if starts_with_vowel_sound(outputEntity):
                        prefixText = 'an '
                    else:
                        prefixText = 'a '
                    questionName = prefixText + outputEntity + value[0]

                    for idx, row in queryResult.iterrows():
                        item = row['item.value'].rsplit('/', 1)[1]
                        attr = db.getIntAttributeOfEntity(item, p)
                        if attr is not None and int(attr) > value[1]:
                            if 'date.value' in row and str(row['date.value'])[:4] != "nan":
                                date = int(str(row['date.value'])[:4])
                            elif 'start.value' in row:
                                date = int(str(row['start.value'])[:4])
                            else:
                                continue
                            count = 1
                            if date in yearCount:
                                count = yearCount[date]
                                count += 1
                                total += 1
                            yearCount.update({date: count})
                            for country in getCountryByEntitiy(item):
                                dateList = list()
                                if country in countryDates:
                                    dateList = countryDates[country]
                                dateList.append(date)
                                countryDates.update({country: dateList})
                            if 744913 == entity:
                                for operator in getAttributeByEntitiy(item, 'P137'):
                                    dateList = list()
                                    if operator in operatorDates:
                                        dateList = operatorDates[operator]
                                    dateList.append(date)
                                    operatorDates.update({operator: dateList})

                    countQuestionEntityEvent(countryDates, questionName, "in ")
                    if 744913 == entity:
                        countQuestionEntityEvent(operatorDates, questionName, "by ")

                    fiveYears = 0
                    tmpYearCount = 0
                    fiveYearsTime = 0
                    print(yearCount)

                    for key in yearCount:
                        if tmpYearCount < 5:
                            if  yearCount[key] > 0:
                                fiveYearsTime += 1
                            fiveYears += yearCount[key]
                            tmpYearCount += 1
                        else:
                            tmpQuestionTemplate = question_template.replace("[EVENT]", questionName)
                            tmpQuestionTemplate = tmpQuestionTemplate.replace("[TIME]",
                                                                              "between " + str(key - 5) + " and " + str(
                                                                                  key - 1))
                            json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                                 ' "answer": ' + json.dumps(
                                fiveYears) + ',' \
                                             ' "type": ' + json.dumps(type) + '},'


                            db.write_answer(type + [9], tmpQuestionTemplate, [fiveYears], [outputEntityId], None, None, [datetime.strptime(str(key - 5) + '-01-01', '%Y-%m-%d').date(), datetime.strptime(str(key - 1) + '-12-31', '%Y-%m-%d').date()])
                            tmpQuestionTemplate = tmpQuestionTemplate.replace("How often","In how many years")

                            db.write_answer(type, tmpQuestionTemplate, [tmpYearCount], [outputEntityId], None, None, [datetime.strptime(str(key - 5) + '-01-01', '%Y-%m-%d').date(), datetime.strptime(str(key - 1) + '-12-31', '%Y-%m-%d').date()])

                            fiveYears = yearCount[key]
                            tmpYearCount = 1
                            fiveYearsTime = 0
                        tmpQuestionTemplate = question_template.replace("[EVENT]", questionName)
                        tmpQuestionTemplate = tmpQuestionTemplate.replace("[TIME]", "in " + str(key))
                        json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                             ' "answer": ' + json.dumps(
                            yearCount[key]) + ',' \
                                              ' "type": ' + json.dumps(type) + '},'
                        print(json_data)
                        db.write_answer(type, tmpQuestionTemplate, [yearCount[key]], [outputEntityId], None, None,[datetime.strptime(str(key) + '-01-01', '%Y-%m-%d').date(), datetime.strptime(str(key) + '-12-31', '%Y-%m-%d').date()])

                    tmpQuestionTemplate = question_template.replace("[EVENT]", questionName)
                    tmpQuestionTemplate = tmpQuestionTemplate.replace("[TIME]", "between 1987 and 2007 ")
                    json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                                         ' "answer": ' + json.dumps(
                        total) + ',' \
                                 ' "type": ' + json.dumps(type) + '},'
                    print(json_data)
                    db.write_answer(type, tmpQuestionTemplate, [total], [outputEntityId], None, None,  [datetime.strptime('1987-01-01', '%Y-%m-%d').date(), datetime.strptime('2007-12-31', '%Y-%m-%d').date()])



