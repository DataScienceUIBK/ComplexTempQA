#!/usr/bin/python
import psycopg2
from configparser import ConfigParser
import requests


def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def write_db(query):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute(query)
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def read_db(query):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute(query)

        data = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()

        # return result
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def read_input():
    return read_db('SELECT * FROM "Input" where id > 205')


def read_spraql_input():
    return read_db('SELECT * FROM  "Input" '
                   'JOIN "Input_SPARQL" ON "Input_SPARQL".input_id = "Input".id '
                   'JOIN "SPARQL_Template" ON "SPARQL_Template".id = "Input_SPARQL".sparql_id ')#where  "Input".id > 412')


def read_template_question_by_input(input_id):
    return read_db('SELECT * FROM "Question_Template" '
                   'JOIN "Input_Question_Template" ON "Input_Question_Template".question_id = "Question_Template".id '
                   'JOIN "Input" ON "Input".id = "Input_Question_Template".input_id '
                   'WHERE "Input".id = ' + str(input_id))


def insert_input(list):
    insert_string = ""
    for prefix, entity, id, descr in list:
        insert_string += "('" + prefix + "'," + str(entity) + "," + str(id) + ",'" + str(descr) + "'),"
    insert_string = insert_string[:-1] + ";"

    query = 'Insert Into "Input" (prefix,entity,id,description) VALUES ' + insert_string + ";"
    #print(query)
    # read_db(query)


def read_event_by_country(country, continent):
    continentStatment = ""
    if continent is not None:
        continentStatment = ' or "continent" = ' + "'" + continent + "'"
    return read_db('select * from "Events2"' +
                   ' where  ("Country" =' + " '" + country + "'" + continentStatment
                   + ') AND (("StartDate" >= ' + "'1987-01-01'" + ' AND "EndDate" <= ' + " '2007-12-31' " + ') OR ("PointDate" >= ' + "'1987-01-01'" + ' AND "PointDate" <= ' + " '2007-12-31')) " +
                   'AND "Name" not like ' + " '%19%' " + ' AND "Name" not like ' + " '%200%'")


def read_events():
    return read_db('select * from "Events"' +
                   ' where '#"EventID" > 2418042 and '
                   + ' (("StartDate" >= ' + "'1987-01-01'" + ' AND "EndDate" <= ' + " '2007-12-31' " + ') OR ("PointDate" >= ' + "'1987-01-01'" + ' AND "PointDate" <= ' + " '2007-12-31')) ORDER BY " + ' "EventID" ASC ')


def readAttributeEvents():
    return read_db('select * from "Events_attributes_int"')


#TODO delete
def read_questions(table, add, limit):
    if limit > 0:
        limit = "limit " + str(limit)
    else:
        limit = ""
    return read_db('SELECT setseed(0.42); select * from "' + table + '" ' + add + " ORDER BY random()" + limit)

#TODO delete
def read_questionsNew(table_name, add, batch_size=1000, max_rows=None):
    if max_rows is None:
        query = f'SELECT * FROM "{table_name}" {add} order by id'
    else:
        query = f'SELECT setseed(0.42);  SELECT * FROM "{table_name}" {add} ORDER BY random()'
    offset = 0
    rows_read = 0

    while max_rows is None or rows_read < max_rows:
        # Calculate the batch size for the current iteration
        current_batch_size = min(batch_size, max_rows - rows_read) if max_rows is not None else batch_size
        print(current_batch_size)
        print(offset)
        # Fetch data in batches using LIMIT and OFFSET
        result = read_db(f"{query} LIMIT {current_batch_size} OFFSET {offset}")
        if not result:
            break

        for row in result:
            yield row

        offset += current_batch_size
        rows_read += len(result)

def read_event(eventId):
    return read_db('select "Name", "description"  from "Events2" ' +
                   'where "EventID" = ' + str(eventId))

def readEventPageView(eventId):
    return read_db('select "pageViews"  from "Events2" ' +
                   'where "EventID" = ' + str(eventId))

def readEntityPageView(eventId):
    return read_db('select "pageViews"  from "Entities" ' +
                   'where "EntityID" = ' + str(eventId))

def readEventStddevPageView():
    return read_db('SELECT stddev("pageViews") AS two_times_stddev FROM "Events2"')

def readEntityStddevPageView():
    return read_db('SELECT stddev("pageViews") AS two_times_stddev FROM "Entities"')



def read_countries():
    return read_db('select distinct "Country" From "Events2" where "Country" is not NULL')


def get_name_of_country(id):
    if type(id) == str and id[0] == 'Q':
        id = id[1:]
    result = read_db('select "Name"  from "Countries" where "ID" = ' + str(id))
    if len(result) == 0:
        return getNameOfEntity('Q' + id)
    else:
        return result[0][0]


def getNameOfEntity(entity):
    if entity is not None:
        if entity is int:
            entity = 'Q' + entity
        link = 'https://www.wikidata.org/wiki/Special:EntityData/' + entity + '.json'
        dataJson = requests.get(link).json().get('entities').get(entity).get('labels')
        if 'en' in dataJson:
            return dataJson.get('en').get('value')
        else:
            return None
    else:
        return None

def getNameOfEnties(entity):
    result = []
    for e in entity:
        result.append(getNameOfEntity(e))
    return result

def entityHasProperty(id, property):
    if str(id)[0] != 'Q':
        id = 'Q' + str(id)
    link = 'https://www.wikidata.org/wiki/Special:EntityData/' + id + '.json'
    dataJson = requests.get(link).json().get('entities').get(id)
    return property in dataJson["claims"]


def getAttributeOfEntity(id, property):
    if str(id)[0] != 'Q':
        id = 'Q' + str(id)
    link = 'https://www.wikidata.org/wiki/Special:EntityData/' + id + '.json'
    dataJson = requests.get(link).json().get('entities').get(id)
    claims = dataJson.get("claims")
    if claims:
        property_claims = claims.get(property)
        if property_claims:
            last_claim = property_claims[-1]
            if "mainsnak" in last_claim:
                mainsnak = last_claim["mainsnak"]
                if "datavalue" in mainsnak:
                    datavalue = mainsnak["datavalue"]
                    if "value" in datavalue:
                        return datavalue["value"]["id"]

    return None

def getAttributeOfEntities(id, property):
    if str(id)[0] != 'Q':
        id = 'Q' + str(id)
    link = 'https://www.wikidata.org/wiki/Special:EntityData/' + id + '.json'
    dataJson = requests.get(link).json().get('entities').get(id)
    claims = dataJson.get("claims")
    result = []
    if claims:
        property_claims = claims.get(property)
        if property_claims:
            claims = property_claims
            for c in claims:
                if "mainsnak" in c:
                    mainsnak = c["mainsnak"]
                    if "datavalue" in mainsnak:
                        datavalue = mainsnak["datavalue"]
                        if "value" in datavalue:
                            result.append(datavalue["value"]["id"])

    if len(result) > 0:
        return result
    return None


def getIntAttributeOfEntity(id, property):
    if str(id)[0] != 'Q':
        id = 'Q' + str(id)
    link = 'https://www.wikidata.org/wiki/Special:EntityData/' + id + '.json'
    dataJson = requests.get(link).json().get('entities').get(id)
    claims = dataJson.get("claims")
    if claims:
        property_claims = claims.get(property)
        if property_claims:
            last_claim = property_claims[-1]
            if "mainsnak" in last_claim:
                mainsnak = last_claim["mainsnak"]
                if "datavalue" in mainsnak:
                    datavalue = mainsnak["datavalue"]
                    if "value" in datavalue:
                        value = datavalue["value"]
                        amount = value["amount"]
                        sign = 1
                        if amount[0] == '-':
                            sign = -1

                        if amount[1:].__contains__("."):
                            return float(amount[1:]) * sign
                        else:
                            return int(amount[1:]) * sign
    return None


if __name__ == '__main__':
    print(getAttributeOfEntities('Q20', 'P30')[0])
    #print(read_input())

    #array = [('Q', 1, 2), ('Q', 4, 5)]
    #insert_input(array)

def write_answer3(tax, entityQuestion, entityAnswer,hop, timeframe,countryQuestion, countryAnswer,question,answer,newRating,newID,pageview):
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute("""
           Insert Into "AnswerFinal" (tax_type,entity_question,entity_answer,hop_property, timeframe,country_question,country_answer,question,answer,rating,id,pageviews)
           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
           """, (tax, entityQuestion, entityAnswer,hop, timeframe,countryQuestion, countryAnswer,question,answer,newRating,newID,pageview)
                    )
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
def write_answer4(tax, entityQuestion, entityAnswer,countryQuestion, countryAnswer, hop, question,answer,rating,newID,timeframe,isUnnamed):
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute("""
           Insert Into "AnswerFinal2" (tax_type,entity_question,entity_answer,country_question, country_answer, hop_property, timeframe,question,answer,id,rating,is_unnamed)
           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
           """, (tax, entityQuestion, entityAnswer,countryQuestion, countryAnswer, hop, timeframe,question,answer,newID,rating,isUnnamed)
                    )
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def write_answer2(question,questionString):
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute("""
           Insert Into "AnswerEntity" (tax_type,question,answer,entity_question,entity_answer,timeframe,country_question,country_answer)
           VALUES(%s,%s,%s,%s,%s,%s,%s,%s);
           """, (question.type, questionString, question.answer, question.getQuestionEntities(), question.answer_entity_id, question.timeframe,question.input_country, question.output_country)
                    )
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()



def write_answer(type, questionString, answer, questionEntity, answerEntity, hopProperty, timeframe):
    # for idx, q in enumerate(questionEntity):
    #    if q.__contains__('Q'):
    #        questionEntity[idx] = int(q[1:])
    # if answerEntity is not None:
    #    for idx, q in enumerate(answerEntity):
    #        if q.__contains__('Q'):
    #            answerEntity[idx] = int(q[1:])
    # if hopProperty is not None:
    #    for idx, q in enumerate(hopProperty):
    #        if q.__contains__('P'):
    #            hopProperty[idx] = int(q[1:])

    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute("""
        Insert Into "AnswerEntity" (tax_type,question,answer,entity_question,entity_answer,hop_property,timeframe,country_question,country_answer)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """, (type, questionString, answer, questionEntity, answerEntity, hopProperty, timeframe,None,None)
                    )
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def storeUnnamed(unnamedEvent, id, catId, cId,p):
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        if cId is not None:
            cur.execute("""
              Insert Into "UnnamedEvent" (eventId,name,catId,country,attribute)
            VALUES(%s,%s,%s,%s,%s);
            """, (str(id), str(unnamedEvent), catId, cId,p)
                        )
        else:
            cur.execute("""
                         Insert Into "UnnamedEvent" (eventId,name,catId,attribute)
                       VALUES(%s,%s,%s,%s);
                       """, (str(id), str(unnamedEvent), catId,p)
                        )
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def storeUnnamedEntity(unnamedEvent, id, catId, cId,p):
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()
        # execute a statement
        if cId is not None:
            cur.execute("""
              Insert Into "UnnamedEntity" (eventId,name,catId,country,attribute)
            VALUES(%s,%s,%s,%s,%s);
            """, (str(id), str(unnamedEvent), catId, cId,p)
                        )
        else:
            cur.execute("""
                         Insert Into "UnnamedEntity" (eventId,name,catId,attribute)
                       VALUES(%s,%s,%s,%s);
                       """, (str(id), str(unnamedEvent), catId,p)
                        )
        conn.commit()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


