import db
import SPARQL_reader
import requests

def extractYear(start,end,point):
    year = 0
    if start is not None:
        year = start.year
    elif end is not None:
        if year == 0:
            year = end.year
        elif year != end.year:
            return 0
    elif point is not None:
        if year == 0:
            year = point.year
        elif year != point.year:
            return 0
    return year


def extractFirstCategory(entityId):
    url = "https://www.wikidata.org/wiki/Special:EntityData/Q"+str(entityId)+ ".json"
    response = requests.get(url)
    data = response.json()

    if "entities" in data:
        entity_data = data["entities"].get("Q"+str(entityId))
        if entity_data:
            claims = entity_data.get("claims")
            if claims:
                p31_claims = claims.get("P31")
                if p31_claims:
                    first_claim = p31_claims[0]
                    if "mainsnak" in first_claim:
                        mainsnak = first_claim["mainsnak"]
                        if "datavalue" in mainsnak:
                            datavalue = mainsnak["datavalue"]
                            if "value" in datavalue:
                                value = datavalue["value"]
                                if "id" in value:
                                    return value["id"]

    return None

events = db.read_events()

for id, name, start, end, point, cID, instancesIds, description, continent, pageviews in events:
    attributes = [
        ("P1120", "which resulted in [number] deaths"),
        ("P1339", "which resulted in [number] injured people"),
        ("P1561", "which resulted in [number] survivors"),
        ("P1132", "which had [number] participants"),
        #("P2895", "had a maximum sustained winds of [number] m/s"),
        #("P2532", "had a lowest atmospheric pressure of [number] hPa"),
        ("P1868", "which had [number] ballot(s) cast"),
        ("P1867", "which had [number] eligible voters"),
        ("P1110", "which had [number] spectators"),
        ("P1697", "which had [number] total valid votes"),
        ("P2528", "which had a magnitude of [number] on the Richter magnitude scale"),
        #("P4511", "vertical depth"),
        ("P1350", "which resulted in [number] games played"),
        ("P1351", "which had [number] points scored"),
        ("P3886", "which had [number] perpetrators"),
        ("P8682", "which had [number] negative votes"),
        ("P8683", "which had [number] support votes"),
        ("P710", "where [entity] was participant"),
        ("P1427", "where [entity] was the start point"),
        ("P1444", "where [entity] was the destination point"),
        ("P726", "where [entity] was the candidate"),
        ("P1346", "where [entity] was the winner"),
        ("P533", "where [entity] was the target"),
        ("P664", "where [entity] was the organizer"),
        ("P121", "where [entity] was the operated item"),
        ("P520", "where [entity] was the armament"),
        ("P371", "where [entity] was the presenter"),
        ("P8031", "where [entity] was the perpetrator"),
    ]
    for p, pLabel in attributes:
        print(len(events))

        if db.entityHasProperty(id, p):
            year = extractYear(start,end,point)
            if year > 0:
                catId = extractFirstCategory(id)
                isInt = False
                if pLabel.__contains__("[number]"):
                    attr = db.getIntAttributeOfEntity(id, p)
                    if attr is None:
                        continue
                    attributeText = pLabel.replace('[number]', str(attr))
                    isInt = True
                else:
                    attr = db.getAttributeOfEntity(id, p)
                    if attr is None:
                        continue
                    #print(db.getNameOfEntity(attr))
                    attributeText = pLabel.replace('[entity]', str(db.getNameOfEntity(attr)))

                if attributeText is not None:
                    sparqlResult = SPARQL_reader.checkSPARQL(isInt,catId,year,p,attr)



                    if sparqlResult.shape[0] == 1:
                        result_entity = sparqlResult.iloc[0]['item.value'].rsplit("/", 1)[-1]

                        if result_entity == 'Q' + str(id):

                            cat = db.getNameOfEntity(catId)
                            if cat is None:
                                continue
                            unnamedEvent = cat + " in " + str(year) + " " + attributeText
                            #print(unnamedEvent)
                            db.storeUnnamed(unnamedEvent,id,catId,None,p)
                    else:
                        sparqlResult = SPARQL_reader.checkSPARQL(isInt,catId, year, p, attr, cID)
                        if sparqlResult.shape[0] == 1:
                            result_entity = sparqlResult.iloc[0]['item.value'].rsplit("/", 1)[-1]
                            if result_entity == 'Q' + str(id):

                                cat = db.getNameOfEntity(catId)
                                if cat is None:
                                    continue
                                country = db.getNameOfEntity(cID)
                                if isInt:
                                    attr = db.getIntAttributeOfEntity(id,p)
                                    attributeText = pLabel.replace('[number]', str(attr))

                                else:
                                    attr = db.getAttributeOfEntity(id, p)
                                    attributeText = pLabel.replace('[entity]', str(db.getNameOfEntity(attr)))

                                if country is not None:
                                    unnamedEvent = cat + " in " + str(year) + " in " + country + " " + attributeText
                                    #print(unnamedEvent)
                                    db.storeUnnamed(unnamedEvent, id, catId, cID,p)
