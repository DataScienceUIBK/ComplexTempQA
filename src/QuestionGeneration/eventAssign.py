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
    if claimId in dataJson["claims"]:
        if 'datavalue' in dataJson["claims"][claimId][0]["mainsnak"]:
            value = dataJson["claims"][claimId][0]["mainsnak"]["datavalue"]["value"]["amount"]

            if value.__contains__("+"):
                if value.__contains__("."):
                    value = float(value.replace("+", ""))
                else:
                    value = int(value.replace("+", ""))
            else:
                value = "'" + value + "'"
            return value
    else:
        return -1


def fillClaimsInDb(tableName):
    result = db.read_db('SELECT * FROM "Events"')

    for id, name, start, end, point, cID, instancesIds, description, continent in result:
        print(id)
        link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(id) + '.json'
        dataJson = requests.get(link).json().get('entities').get('Q' + str(id))
        deaths = getClaimById('P1120', dataJson)
        injured = getClaimById('P1339', dataJson)
        survivor = getClaimById('P1561', dataJson)
        participant = getClaimById('P1132', dataJson)
        wind = getClaimById('P2895', dataJson)
        pressure = getClaimById('P2532', dataJson)
        ballot = getClaimById('P1868', dataJson)
        voters = getClaimById('P1867', dataJson)
        attandance = getClaimById('P1110', dataJson)
        votes = getClaimById('P1697', dataJson)
        magnitude = getClaimById('P2528', dataJson)
        depth = getClaimById('P4511', dataJson)
        match = getClaimById('P1350', dataJson)
        points = getClaimById('P1351', dataJson)
        prepetrators = getClaimById('P3886)', dataJson)
        neg_votes = getClaimById('P8682', dataJson)
        sup_votes = getClaimById('P8683', dataJson)

        if deaths > -1 or injured > -1 or survivor > -1 or participant > -1 or wind > -1 or pressure > -1 or ballot > -1 or voters > -1 or attandance > -1 or votes > -1 or magnitude > -1 or depth > -1 or match > -1 or points > -1 or prepetrators > -1 or neg_votes > -1 or sup_votes > -1:

            db.write_db('INSERT INTO "' + tableName + '"("eventId","number_of_deaths","number_of_injured","number_of_survivors","number_of_participants","maximum_sustained_winds","lowest_atmospheric_pressure","total_number_of_ballots_cast","number_of_eligible_voters","number_of_attendance","total_valid_votes"," earthquake_magnitude_on_the_Richter_magnitude_scale","vertical_depth","number_of_matches played/races/starts","number_of_points/goals/set_scored","number_of_perpetrators","number_of_negative_votes","number_of_support_votes") '
                                                  'VALUES (' + str(id) + ',' + str(deaths) + ',' + str(injured) + ',' + str(survivor) + ',' + str(participant) + ',' + str(wind) + ',' + str(pressure) + ',' + str(ballot) + ',' + str(voters) + ',' + str(attandance) + ',' + str(votes) + ',' + str(magnitude) + ',' + str(depth) + ',' + str(match) + ',' + str(points) + ',' + str(prepetrators) + ',' + str(neg_votes) + ',' + str(sup_votes)  + ' )')


fillClaimsInDb("Events_attributes_int")
