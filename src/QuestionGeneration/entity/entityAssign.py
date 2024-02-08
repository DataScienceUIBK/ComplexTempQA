#!/usr/bin/python

import db
import requests


# result = db.read_db('SELECT * FROM "Events"')

# for id, name, start, end, point, country, instances in result:
#   for i in instances:
#      print("(" + str(id) + "," + i[1:] + "),")

def addInstances():
    result = db.read_db('SELECT * FROM "Instances" where "Name" is null')

    for id, name in result:
        link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(id) + '.json'
        outputEntity = requests.get(link).json().get('entities').get("Q" + str(id)).get('labels').get(
            'en').get('value')
        db.write_db('UPDATE "Instances" SET "Name" = ' + "'" + outputEntity.replace("'",
                                                                                    "\'") + "'" + ' WHERE "InstanceID" = ' + str(
            id) + ';')
        print("(" + str(id) + ',"' + outputEntity.replace("'", "\'") + '"),')


def addContinent():
    result = db.read_db('SELECT * FROM "Events" where "Country" is not null and "continent" is null')

    for id, name, start, end, point, cID, instancesIds, description, continent in result:
        link = 'https://www.wikidata.org/wiki/Special:EntityData/' + cID + '.json'
        dataJson = requests.get(link).json().get('entities').get(cID)
        continentID = dataJson["claims"]["P30"][0]["mainsnak"]["datavalue"]["value"]["id"]
        db.write_db('UPDATE "Events" SET "continent" = ' + "'" + continentID + "'" + ' WHERE "EventID" = ' + str(
            id) + ';')
        # print(continentID)


def getAttributeByEvent():
    attributes = dict()

    result = db.read_db('SELECT * FROM "Events"')

    for id, name, start, end, point, cID, instancesIds, description, continent in result:
        link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(id) + '.json'
        dataJson = requests.get(link).json().get('entities').get('Q' + str(id))
        for claim in dataJson['claims']:
            newlink = 'https://www.wikidata.org/wiki/Special:EntityData/' + claim + '.json'
            claimName = requests.get(newlink).json().get('entities').get(claim).get('labels').get('en').get('value')
            # print(dataJson["claims"][claim][0]["mainsnak"])
            if claimName in attributes:
                attributes[claimName] = attributes[claimName] + 1
            else:
                attributes[claimName] = 1

    print(attributes)

def getClaimById(claimId, dataJson):

    try:
        value = dataJson["claims"][claimId][0]["mainsnak"]["datavalue"]["value"]["amount"]
        if value.__contains__("+"):
            if value.__contains__("."):
                value = float(value.replace("+", ""))
            else:
                value = int(value.replace("+", ""))
        else:
            value = "'" + value + "'"
        return value
    except KeyError as e:
        return -1

def getClaimUnit(claimId, dataJson):
    try:
        value = dataJson["claims"][claimId][0]["mainsnak"]["datavalue"]["value"]["unit"]
        return value
    except KeyError as e:
        return ""

def convertDate(date):
    date = date[0:11]
    print(date)
    # Split the date string into year, month, and day
    parts = date.split('-')

    if len(parts) != 3:
        # Not a valid date format
        return date_str

    year, month, day = parts

    # Check if the month or day is "00" and replace it with "01"
    if month == "00":
        month = "01"
    if day == "00":
        day = "01"

    # Reconstruct the corrected date string
    corrected_date = f"{year}-{month}-{day}"
    print(corrected_date)
    return corrected_date

def getClaimByDate(claimId, dataJson):
    try:
        value = dataJson["claims"][claimId][0]["mainsnak"]["datavalue"]["value"]["time"]
        value = value[1:11]
        return convertDate(value)
    except KeyError as e:
        return None


def getClaimByheritageDate(claimId, dataJson):
    try:
        value = dataJson["claims"][claimId][0]["qualifiers"]["P580"][0]["datavalue"]["value"]["time"]
        return convertDate(value)
    except KeyError as e:
        return None

def nullOrValue(val):
    if val is None:
        return "null"
    else:
        return "'" + val + "'";

def fillClaimsInDb(table_name):
    #result = db.read_db('SELECT "EntityID" FROM "Entities"')
    result = db.read_db('SELECT "EntityID" FROM "Entities" e LEFT JOIN entity_attributes_comp  a ON e."EntityID" = a.qid where a.name is null')
    #result = db.read_db('''
    #SELECT "EntityID"
#FROM "Entities" e
#LEFT JOIN entity_attributes_comp  a ON e."EntityID" = a.qid
#WHERE a.qid IS NULL;
#''')

    for id in result:
        id = id[0]
        link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(id) + '.json'
        dataJson = requests.get(link).json().get('entities').get('Q' + str(id))
        inception = getClaimByDate('P571', dataJson)
        publication_date = getClaimByDate('P577', dataJson)
        heritage_designation_date = getClaimByheritageDate('P1435', dataJson)
        date_of_birth = getClaimByDate('P569', dataJson)
        floors_above_ground = getClaimById('P1101', dataJson)
        duration = getClaimById('P2047', dataJson)
        cost = getClaimById('P2130', dataJson)
        cost_currency = "'" + getClaimUnit('P2130', dataJson) + "'"
        elevation_above_sea_level = getClaimById('P2044', dataJson)
        height = getClaimById('P2048', dataJson)
        area = getClaimById('P2046', dataJson)
        name = db.getNameOfEntity('Q' + str(id))
        print(name)
        if name is not None:
            #query = "UPDATE "+ table_name +" SET name = '" + str(name.replace("'","''")) +"' WHERE qid =  "+ str(id) +" ;"
            query = 'INSERT INTO ' + table_name + '(qid, inception, publication_date, heritage_desg_date, birthday, floors, duration, cost, elevation, height, area,cost_currency,name)' + \
            'VALUES (' + str(id) + ',' + nullOrValue(inception) + ',' + nullOrValue(publication_date) + ',' + nullOrValue(heritage_designation_date) + ',' + nullOrValue(date_of_birth) + ',' + str(floors_above_ground) + ',' + str(duration) + ',' + str(cost) + ',' + str(elevation_above_sea_level) + ',' + str(height) + ',' + str(area) + ',' + str(cost_currency) + ",'" + str(name.replace("'","''"))+"' );"

            db.write_db(query)

fillClaimsInDb("entity_attributes_comp")
