import db

thresholdEvent = db.readEventStddevPageView()[0]
thresholdEntity = db.readEntityStddevPageView()[0]

def populateDicts(list):
    return {entry[1]: entry[0] for entry in list}

def readEventPageView():
    return db.read_db('select "pageViews", "EventID"  from "Events2" ')

def readEntityPageView():
    return db.read_db('select "pageViews", "EntityID"  from "Entities"')

eventDict = populateDicts(readEventPageView())
entityDict = populateDicts(readEntityPageView())

def readPageView(entity, isEvent):
    if isEvent:
        if entity in entityDict:
            return entityDict[entity]
        else:
            return None
    else:
        if entity in eventDict:
            return eventDict[entity]
        else:
            return None



def calculateRating(entities,isEvent,isUnnamed):
    if isUnnamed:
        return 1
    else:
        tmpRating = 1
        if isEvent:
            for e in entities:
                tmp = readPageView(e,True)
                if tmp is None:
                    return 1
                threshold = thresholdEvent
                if tmp >= threshold[0]:
                    tmpRating = 0
                else:
                    return 1
        else:
            for e in entities:
                tmp = readPageView(e,True)
                if tmp is None:
                    return 1
                threshold = thresholdEvent
                if tmp >= threshold[0]:
                    tmpRating = 0
                else:
                    return 1

        return tmpRating

def isUnnamed(question,isEvent):
    if isEvent:
        #for e in events:
        #    query = f'SELECT name from "UnnamedEvent" where eventid =' + f" {e}"
        #    database_data = db.read_db(f"{query}")
        #    if len(database_data) > 0 and question.__contains__(database_data[0][0]):
        #        return True
        #TODO better via string compare:
        keywords = ["ship collision in","earthquake in","Winter Olympic Games in","battle in","shootout in","Chilean presidential election in","Super Bowl in","murder in","homicide in","Australian federal election in","gas explosion in","Eurovision Song Contest edition in","mountaineering accident in","Swedish general election in","United States presidential election in","aircraft shootdown in","legislative election in","presidential election in","edition of the UEFA European Championship in","attempted coup d'état in","amok in","fusillade in","East German general election in","self-coup in","San Marino Grand Prix in","revolution in","aviation accident in","United States presidential inauguration in","bomb attack in","Belgian Grand Prix in","terrorist attack in","car bombing in","structure fire in","sports season in","international incident in","Russian presidential election in","civil war in","ethnic riot in","phreatic eruption in","flood in","Greek legislative election in","attempted murder in","explosion in","environmental disaster in","suicide attack in","incident in","Colombian presidential election in","avalanche in","train fire in","coup d'état in","Danish parliamentary election in","mass shooting in","pogrom in","treaty in","Wikimedia list article in","military operation in","independence referendum in","chess game in","assassination in","stampede in","aircraft hijacking in","FIFA Women's World Cup Final in","occurrence in","ceasefire in","riot in","coordinated terrorist attack in","United Kingdom general election in","protest march in","Academy Awards ceremony in","demonstration in","war in","mass murder in","UEFA Euro Final in","referendum in","Italian general election in","suicide bombing in","South Korean presidential election in","bank robbery in","tornado in","air show accident or incident in","tennis event in","jubilee in","flight in","protest in","suicide car bombing in","association football final in","Japanese House of Representatives election in","Summer Olympic Games in","accidental death in","Brazilian presidential election in","self-immolation in","train wreck in","Bulgarian presidential election in","wildfire season in","conflagration in","final of the FIFA World Cup in","conflict in","golden jubilee in","peace treaty in","Bundestag election in","Polish presidential election in","structural failure in","shipwrecking in","mudflow in","derailment in","referendums in","school shooting in","Betty Barclay Cup in","Argentine presidential election in","royal wedding in","UEFA Champions League final in","collision in","aircraft crash in","airliner bombing in","airstrike in","oil spill in","criminal case in","massacre in","maritime disaster in","megathrust earthquake in","disaster in"]
    else:
        keywords = ["produced by","founded by", "designed by", "written by" ,"directed by", "the movie where the actors"]


    for keyword in keywords:
        if keyword in question:
            return 1

    return 0



def process(list):
    # not needed if count
    for entityQuestion, entityAnswer, countryQuestion, countryAnswer, hop, question, answer, rating, id, tax_type, timeframe, pageviews  in list:

        unnamed = isUnnamed(question,  tax_type.__contains__('a'))

        # count always hard
        if tax_type.__contains__('3'):
            rating = 1
        else:
            rating = calculateRating(entityQuestion, tax_type.__contains__('a'), unnamed)

        #print(unnamed)
        #print(rating)
        #print(question)
        db.write_answer4(tax_type, entityQuestion, entityAnswer,countryQuestion, countryAnswer, hop,  question,
                         answer, rating, id, timeframe,unnamed)




query = f'SELECT *  FROM "AnswerFinal" where id > 18881804 order by id'

offset = 0
rows_read = 0
batch_size = 1000

while True:
        # Fetch data in batches using LIMIT and OFFSET
    result = db.read_db(f"{query} LIMIT {batch_size} OFFSET {offset}")
    if not result:
        break

        # Process the batch of rows
    process(result)

    offset += batch_size
    rows_read += len(result)
