import json
import re
from datetime import datetime
import db
import requests
from bs4 import BeautifulSoup
import sys
import cProfile

import time

errorString = ""

thresholdEvent = db.readEventStddevPageView()[0]
thresholdEntity = db.readEntityStddevPageView()[0]
toJSON = False

entityCountry = dict()
entityTime = dict()
wikiEntityQuestion = dict()
wikiEntityAnswer = dict()

def removeLetters(entity):
    if entity is None:
        return []
    # Remove letters from strings and keep only the numerical part
    result = []
    for e in entity:
        if type(e) == str:
            result.append(int(''.join(filter(str.isdigit, e))))
        else:
            result.append(e)
    #numeric_list = [''.join(filter(str.isdigit, string)) for string in entity]
    # Convert the list of strings to a list of integers
    return result
    #return [int(num) for num in numeric_list]

def get_qid_from_wikipedia(wikipedia_url):
    response = requests.get(wikipedia_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the link to the Wikidata item
        wikidata_link = soup.find('a', href=lambda x: x and 'Special:EntityPage/Q' in x)
        if wikidata_link:
            # Extract the QID from the href attribute
            qid = wikidata_link['href'].split('/')[-1]
            return qid.split('#')[0]

    return None

def getEntityFromAnswer(answer):
    result = []
    for a in answer:
        if a == 'true' or a == 'false' or a is None or a.isdigit():
            return []
        tmp = get_qid_from_wikipedia("https://en.wikipedia.org/wiki/" + a.replace(" ","_"))
        if tmp !=  None:
            result.append(tmp)
    return result

def getCountry(entityQuestion,wikiEntities):
    return []
    if entityQuestion is None:
        return None
    result = []
    for entity in entityQuestion:
        if entity in entityCountry:
            result.append(entityCountry[entity])
        else:
            tmp = None
            claims =  wikiEntities[entity]
            if claims:
                tmp = extractClaim(claims, 'P17')
            if tmp is not None:
                country = removeLetters([tmp])[0]
                result.append(country)
                entityCountry[entity]=country
    return result

def getPageView(entity,tax):
    pageview = 0
    if tax.__contains__('a'):
        for e in entity:
            tmp = db.readEventPageView(e)
            if len(tmp) > 0 and tmp[0][0] is not None:
                if pageview is None or tmp[0][0] < pageview:
                    pageview = tmp[0][0]
        threshold = thresholdEvent
    if tax.__contains__('b'):
        for e in entity:
            tmp = db.readEntityPageView(e)
            if len(tmp) > 0 and tmp[0][0] is not None:
                if pageview is None or tmp[0][0] < pageview:
                    pageview = tmp[0][0]
        threshold = thresholdEntity
    return pageview

def getRating(entity, tax,pageview):
    threshold = 0

    if tax.__contains__('a'):
        threshold = thresholdEvent
    if tax.__contains__('b'):
        threshold = thresholdEntity
    if pageview is not None:
        if pageview >= threshold[0]:
            return 0
        else:
            return 1
    else:
        return 1

def extractClaim(claims, property):
    # Iterate over each claim
    property_claims = claims.get(property)
    if property_claims:
        claims = property_claims
        for c in claims:
            if "mainsnak" in c:
                mainsnak = c["mainsnak"]
                if "datavalue" in mainsnak:
                    datavalue = mainsnak["datavalue"]
                    if "value" in datavalue:
                        times = datavalue["value"]["time"][1:12]
                        times = times.replace('00-00T', '01-01')
                        times = times.replace('00T', '01')
                        return times.replace('T','')

def getTimeframe(entities, wikiEntities):
    result = []
    for entity in entities:
        if entity in entityTime:
            result.extend(entityTime[entity])
        else:
            try:
                #link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(entity) + '.json'
                #data = requests.get(link).json().get('entities').get('Q' + str(entity))

                claims = wikiEntities[entity]
                if claims:

                    # Check if the claim is for a date (P585 is the property ID for point in time)
                    start = list()
                    point = list()
                    end = list()
                    start.append(extractClaim(claims, 'P580'))
                    point.append(extractClaim(claims,'P577'))
                    if all(x is None for x in point):
                        point.append(extractClaim(claims,'P585'))
                    if not all(x is None for x in point):
                        if all(x is None for x in start):
                            start.append(extractClaim(claims,'P571'))
                        if all(x is None for x in start):
                            start.append(extractClaim(claims,'P569'))


                        end.append(extractClaim(claims, 'P576'))
                        if all(x is None for x in end):
                            end.append(extractClaim(claims,'P582'))
                        if all(x is None for x in end):
                            end.append(extractClaim(claims, 'P570'))
                    start.extend(end)
                    start.extend(point)
                    entityTime[entity] = start

                    result.extend(start)
            except json.JSONDecodeError as e:
                global errorString
                errorString += e
                return []
    return  [x for x in result if x is not None]


def taxHelper(number):

    if number == 1:
        return "1a"
    elif number == 2:
        return "1b"
    elif number == 3:
        return "1c"
    elif number == 4:
        return "2a"
    elif number == 5:
        return "2b"
    elif number == 6:
        return "2c"
    elif number == 7:
        return "3a"
    elif number == 8:
        return "3b"
    elif number == 9:
        return "3c"

def addTax(curTax, question):
    if curTax.__contains__('c'):
        return curTax
    else:
        if question.__contains__('happen before') or question.__contains__('happen after') or question.__contains__('first,') or question.__contains__('first?'):
            return curTax + 'c'
        return curTax

def toPast(question):
    question=question.replace('have','had')
    question=question.replace('happen','happened')
    return question

def extract_combinations(input_str):
    # Use regular expression to find letter combinations
    numbers = re.findall(r'\d', input_str)
    letters = re.findall(r'[a-zA-Z]', input_str)
    if not all(element == numbers[0] for element in numbers):
        global errorString
        errorString += 'different taxonomy '
    return numbers[0] + ''.join(letters)


def getnewTax(tax):
    result = ""
    for t in tax:
        result += taxHelper(t)
    return extract_combinations(result)


def reorderTime(date_objects):
    # Convert date strings to datetime objects
    if date_objects is not None and type(date_objects[0]) == str:
        date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in date_objects]

    # Ensure the first date is lower than the second
    #date_objects = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in date_objects]
    sorted_dates = sorted(date_objects)

    return [sorted_dates[0].strftime('%Y-%m-%d'),sorted_dates[-1].strftime('%Y-%m-%d')]

def addQuestionMark(question):
    question = question.replace('?','')
    question = question.replace('acting with','appear in a movie with')
    question = question.replace('write in','wrote')
    question = question.replace('produce in','produced')
    question = question.replace('design in','designed')
    question = question.replace('direct in','directed')
    question = question.replace('higher the number','higher number')
    question = question.replace('lower the number','lower number')
    question = question.replace('  ',' ')
    return question + '?'

def skipQuestion(question):
    if question.__contains__("In how many years "):
        if not question.__contains__("between"):
            return True
    return False

def flatten_list(input_list):
    if isinstance(input_list, list) and len(input_list) == 1 and isinstance(input_list[0], list):
        # If it's a nested list, flatten it
        return input_list[0]
    else:
        # Otherwise, return the input as is
        return input_list

def fixTax(tax,question):
    if len(tax) == 1 and tax[0] == 4:
        if not (question.__contains__("higher") or question.__contains__("lower")):
            return [1]
    return tax

def populateWikiEnityAnswer(entities,target,lookup):
    for entity in entities:
        if entity not in target:
            if entity in lookup:
                target[entity] = lookup[entity]
            else:
                link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(entity) + '.json'
                data = requests.get(link).json().get('entities').get('Q' + str(entity))
                claims = data.get("claims")
                target[entity] = claims
    return target

def listToJSON(questionList, startID):
    global wikiEntityQuestion
    global wikiEntityAnswer
    #else:
    #    print('id;type;question;give answer')
    for tax, entityQuestion,entityAnswer,countryQuestion,countryAnswer,hop,timeframe,question,answer,rating,id,newID in questionList:
        global errorString

        errorString = ""




        tax = fixTax(tax,question)
        tax = getnewTax(tax)
        tax = addTax(tax, question)

        question = toPast(question)
        question = addQuestionMark(question)
        entityQuestion = removeLetters(entityQuestion)
        entityAnswer = removeLetters(entityAnswer)
        countryQuestion = removeLetters(countryQuestion)
        countryAnswer = removeLetters(countryAnswer)
        hop = removeLetters(hop)
        answer = flatten_list(answer)

        if answer is None or len(answer) == 0:
            continue

        if len(entityAnswer) == 0:
            try:
                entityAnswer = getEntityFromAnswer(answer)
            except:
                time.sleep(10)
                entityAnswer = getEntityFromAnswer(answer)



        if len(countryQuestion) == 0 and (entityQuestion is not None and len(entityQuestion) > 0):
            #if len(wikiEntityQuestion) == 0:
            #    wikiEntityQuestion = populateWikiEnityAnswer(entityQuestion,wikiEntityQuestion,wikiEntityAnswer)
            countryQuestion = getCountry(entityQuestion,wikiEntityQuestion)

        if len(countryAnswer) == 0 and (entityAnswer is not None and len(entityQuestion) > 0):
            #if len(wikiEntityAnswer) == 0:
            #    wikiEntityAnswer = populateWikiEnityAnswer(entityAnswer,wikiEntityAnswer,wikiEntityQuestion)
            countryAnswer = getCountry(entityAnswer,wikiEntityAnswer)

        #timeframe
        if timeframe is None and entityQuestion is not None:
            if not all(e in wikiEntityQuestion for e in entityQuestion):
                wikiEntityQuestion = populateWikiEnityAnswer(entityQuestion,wikiEntityQuestion,wikiEntityAnswer)
            timeframe = getTimeframe(entityQuestion, wikiEntityQuestion)

        #reorder timeframe
        if timeframe is not None and len(timeframe) > 0:
            timeframe = reorderTime(timeframe)

        #0 easy , 1 hard
        if entityQuestion is None:
            newRating = 1
            pageView = 0
        else:
            pageView = getPageView(entityQuestion, tax)
            newRating = getRating(entityQuestion, tax,pageView)


        entityQuestion = removeLetters(entityQuestion)
        entityAnswer = removeLetters(entityAnswer)
        countryQuestion = removeLetters(countryQuestion)
        countryAnswer = removeLetters(countryAnswer)
        #TODO remove reudancy  the company the bank, the movie the movie, the book the book
        #TODO remove reduancy in answer too the movie the movie
        skip = skipQuestion(question)

        if not skip:
            s = ""
            if errorString == "":

                if toJSON:
                    s = f'{{"id":{startID},"question":"{question}",'
                    s += f'"answer":{json.dumps(answer)},'
                    s += f'"type":"{tax}",'
                    s += f'"rating":{newRating}'
                    if timeframe:
                        s += f',"timeframe":{json.dumps(timeframe)}'
                    if entityQuestion:
                        s += f',"question_entity":{json.dumps(entityQuestion)}'
                    if entityAnswer:
                        s += f',"answer_entity":{json.dumps(entityAnswer)}'
                    if countryQuestion:
                        s += f',"question_country_entity":{json.dumps(countryQuestion)}'
                    if countryAnswer:
                        s += f',"answer_country_entity":{json.dumps(countryAnswer)}'
                    if hop:
                        s += f',"hops":{json.dumps(hop)}'
                    s += '}'
                    startID += 1
                else:
                    #s = (f'{id};{tax};{question};{answer}')
                    print(newID)
                    db.write_answer3(tax, entityQuestion, entityAnswer,hop, timeframe,countryQuestion, countryAnswer,question,answer,newRating,newID,pageView)
            else:
                print("ERROR at ID:"+ id + " " + errorString)
                if toJSON:
                    s = ("ERROR at ID:"+ id + " " + errorString)

            if toJSON:
                with open(file_path, 'a') as file:
                    file.write(s+'\n')
    return startID


table =  sys.argv[1]
limit = sys.argv[2]
if sys.argv[3] == '0':
    array = ""
else:
    array = "where (tax_type = ARRAY["
    for arg in sys.argv[3:-1]:
            array += arg+","
    array = array[:-1]+'])'
file_path = sys.argv[-1]


#events = db.read_questions(table,array,int(limit))

#if toJSON:
#    with open(file_path, 'a') as file:
#        file.write('[\n')
#listToJSON(events,1)


#if toJSON:
#    with open(file_path, 'a') as file:
#        file.write(']')

if int(limit) > 0:
    max_rows = int(limit)
else:
    max_rows = None
counter = 1
if toJSON:
    with open(file_path, 'a') as file:
        file.write('[\n')

if max_rows is None:
    query = f'SELECT "{table}".*  FROM "{table}" LEFT JOIN "AnswerFinal" ON "{table}"."ID" = "AnswerFinal".id WHERE "AnswerFinal".id IS NULL order by "ID"'

    #query = f'SELECT * FROM "{table}" {array} where "ID" > 29029927 order by "ID"'
    #query = f'SELECT * FROM "{table}" {array} where "ID" IN(29097366, 29099425, 29192874, 29201071, 29099424, 29168367, 29166265) order by "ID"'
else:
    query = f'SELECT setseed(0.42);  SELECT * FROM "{table}" {array} ORDER BY random()'

print(query)
offset = 0
rows_read = 0
batch_size = 1000

while max_rows is None or rows_read < max_rows:
        # Fetch data in batches using LIMIT and OFFSET
    result = db.read_db(f"{query} LIMIT {batch_size} OFFSET {offset}")
    if not result:
        break

        # Process the batch of rows
    counter = listToJSON(result,counter)

    offset += batch_size
    rows_read += len(result)



if toJSON:
    with open(file_path, 'a') as file:
        file.write(']')


