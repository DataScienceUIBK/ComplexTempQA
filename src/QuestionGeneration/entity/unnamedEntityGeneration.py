import db
import SPARQL_reader
import requests

def extractYear(start,end):
    year = 0
    if start is not None:
        year = start.year
    elif end is not None:
        if year == 0:
            year = end.year
        elif year != end.year:
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

def getUnit(attr):
    # Check if 'P1630' (formatter URL) is present in the entity data
    if attr in entity_data.get('claims', {}):
        # Retrieve the formatter URL for the unit
        formatter_url = entity_data['claims'][attr][0]['mainsnak']['datavalue']['value']

        # Extract the unit from the formatter URL
        unit = formatter_url.split('/')[-1]

        return db.getNameOfEntity(unit)

entities = db.read_db('SELECT "EntityID", "Name", "StartDate", "EndDate", category FROM "Entities" where "EntityID" > 720357 order by "EntityID"')

for id, name, start, end, cat  in entities:
    attributes = [
        ("person", ["P17"], " of [e1] in [year]"),

        ("movie", ["P57","P162"], " directed by [e1] and produced by [e2] in [year]"),
        ("movie", ["P136","P2047"], " with the genre of [e1] with a duration of [e2] in [year]"),
        ("movie", ["P161"], " where the actors [e] played"),  # special case

        ("book", ["P50"], " written by [e1] in [year]"),

        ("company", ["P112"], " founded by [e1] in [year]"),

        ("building", ["P84"], " which is designed by the architect [e1] in [year]"),

    ]
    for pCat, pProp, pString in attributes:
        if cat == pCat:
            if db.entityHasProperty(id, pProp[0]):
                catId = extractFirstCategory(id)

                if pProp[0] == 'P161': #movie special case
                    attr = list()
                    attrEnti = db.getAttributeOfEntities(id,  pProp[0])
                    if attrEnti is not None and len(attrEnti) > 1:
                        attr.append(attrEnti[0])
                        attr.append(attrEnti[1])
                        sparqlResult = SPARQL_reader.checkSPARQLEntity(catId, pProp[0], attr)
                        if sparqlResult.shape[0] != 1:
                            if len(attrEnti) > 2:
                                attr.append(attrEnti[2])
                                sparqlResult = SPARQL_reader.checkSPARQLEntity(catId, pProp[0], attr)
                                if sparqlResult.shape[0] != 1:
                                    continue
                            else:
                                continue
                    else:
                        continue
                    answerString = ""
                    for index, value in enumerate(attr):
                        if index == 0:
                            answerString += db.getNameOfEntity(value)
                        elif index == len(attr)-1:
                            answerString += " and " + db.getNameOfEntity(value)
                        else:
                            answerString += ", " +db.getNameOfEntity(value)


                    pString = pString.replace("[e]", answerString)
                    unnamedEvent = "the " + cat + pString

                    #print(unnamedEvent)
                    db.storeUnnamedEntity(unnamedEvent, id, catId, None, attr)

                else:
                    year = extractYear(start, end)
                    if year is not None and year > 0:
                        attr = list()
                        for p in pProp:
                            if p == 'P2047':
                                attr.append(str(db.getIntAttributeOfEntity(id, p)))
                            else:
                                attr.append(db.getAttributeOfEntity(id, p))

                        sparqlResult = SPARQL_reader.checkSPARQLEntity(catId,pProp[0],attr,year)
                        if sparqlResult.shape[0] == 1:
                            cat = db.getNameOfEntity(catId)
                            if cat is None:
                                continue

                            for i, item in enumerate(attr):
                                #if item == 'P2048':
                                #    unit = getUnit(item)
                                 #    pString = String.replace("[e" + str(i) + "]", db.getNameOfEntity(item) + " " + unit)
                                #else:
                                pString = pString.replace("[e" + str(i+1) +"]",db.getNameOfEntity(item))
                            pString = pString.replace("[year]", str(year))
                            unnamedEvent = "the " + cat + pString

                            #print(unnamedEvent)
                            db.storeUnnamedEntity(unnamedEvent, id, catId, None, attr)


