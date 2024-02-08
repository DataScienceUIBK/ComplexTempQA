import db
import SPARQL_reader


entities =  db.read_db('SELECT "EntityID", "Name" FROM "Entities" where category like ' + "'person' order by " + '"EntityID"')

for entityid, entity in entities:
    s = '''
    SELECT distinct ?cat
    WHERE {
      ?cat wdt:P161 ?entity;


      FILTER(?entity = wd:[ENTITY])}
    '''
    s = s.replace('[ENTITY]', 'Q' + str(entityid))
    results_df2 = SPARQL_reader.readSPARQL(s, "")
    print(entityid)
    if len(results_df2) > 0:
        db.write_db('UPDATE "Entities" SET "isActor" = true WHERE "EntityID" = ' + str(entityid))
        #print(entityid)