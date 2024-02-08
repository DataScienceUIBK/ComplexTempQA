from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import sys
import requests
import db
import SPARQL_reader
import json
import datetime
import time
import SPARQLGenerator2
from datetime import datetime
import re
import nltk  # $ pip install nltk
from nltk.corpus import cmudict  # >>> nltk.download('cmudict')
from datetime import date
import time
from question import Question


question_template_general = "How many [GENRE][CAT] [ADDITIONAL] did [ENTITY] [DO] [YEAR]?"
question_template_actor = "How many times did [ENTITY1] acting with [ENTITY2] [YEAR] [ADDITIONAL]?"

question_template_general_time = "In how many years did [ENTITY] [DO] in [GENRE][CAT] [ADDITIONAL] [YEAR]?"
question_template_actor_time = "In how many years did [ENTITY1] acting with [ENTITY2] [YEAR] [ADDITIONAL]?"


def createGeneralQuestion(entityid, entity,verb,yearStart,yearEnd,additional,cat,genre,answer,template,type):
    year = "between " + str(yearStart) + " and " + str(yearEnd)
    tmpQuestionTemplate = template.replace("[ENTITY]", entity)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[DO]", verb)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[YEAR]", year)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[CAT]", cat)
    if genre != '':
        genre += ' '
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[GENRE]", genre)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ADDITIONAL]", additional)

    question = Question(False, (entityid, entity), [str(answer)], [8], timeframe=[str(yearStart) + '-01-01' ,str(yearEnd) + '-12-31'])
    question.createQuestion(tmpQuestionTemplate)
    #db.write_answer(type, tmpQuestionTemplate, [answer], ['Q' + str(entityid)], None,None, None)

def createActorQuestion(entityid1, entity1,entity2id, entity2,yearStart,yearEnd,additional,answer,template,type):
    year = "between " + str(yearStart) + " and " + str(yearEnd)
    tmpQuestionTemplate = template.replace("[ENTITY1]", entity1)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ENTITY2]", entity2)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[YEAR]", year)
    tmpQuestionTemplate = tmpQuestionTemplate.replace("[ADDITIONAL]", additional)

    question = Question(False, (entityid1, entity1), [str(answer)], [8], entity2=(entity2id,entity2), timeframe=[str(yearStart) + '-01-01' ,str(yearEnd) + '-12-31'])
    question.createQuestion(tmpQuestionTemplate)
    #db.write_answer(type, tmpQuestionTemplate, [answer], ['Q' + str(entityid1), 'Q' + str(entity2id)], None,None, None)


attributes = [
    ('direct','P57','movies','Q11424'),
    ('act','P161','movies','Q11424'),
    ('produce','P162','movies','Q11424'),
    ('write','P50','books','Q7725634'),
    ('design','P84','building','Q811979')
    ]

genre = [
    ('action','Q188473'),
    ('drama','Q130232'),
    ('comedy','Q157443'),
    ('action','Q2484376'),
    ('thriller','Q959790')
]


def getCoActors(entity):
    s = '''
    SELECT ?coActor ?date
WHERE {
  ?cat wdt:P31 wd:Q11424;
       wdt:P577 ?date.
  ?cat wdt:P161 wd:[ENTITY].
  ?cat wdt:P161 ?coActor.
  
  FILTER (?coActor != wd:[ENTITY])  # Exclude the actor himself
  
  BIND(YEAR(?date) AS ?year)
  FILTER(YEAR(?date) >= 1987 && YEAR(?date) <= 2007) 

}
GROUP BY ?coActor ?date
ORDER BY ?coActor

    '''
    s = s.replace('[ENTITY]', 'Q' + str(entity))
    #s = s.replace('[ENTITY]', 'Q' + str(entity))

    try:
        results_df = SPARQL_reader.readSPARQL(s, "")
    except:
        time.sleep(60)
        results_df = SPARQL_reader.readSPARQL(s, "")


    return results_df



def createQuery(cat,date,entity,do,genre,add):
    s = '''
    SELECT distinct ?cat ?year (GROUP_CONCAT(DISTINCT ?genre; SEPARATOR=" ") AS ?genres)
    WHERE {
      ?cat wdt:P31 wd:[CAT];
           wdt:[DATE] ?date.
      ?cat wdt:[DO] wd:[ENTITY].
      OPTIONAL {
    ?cat wdt:P136 ?genre.
    }
      [ADD]
      BIND(YEAR(?date) AS ?year)
      FILTER(YEAR(?date) >= 1987 && YEAR(?date) <= 2007) 
    '''
    s = s.replace('[CAT]', cat)
    s = s.replace('[DATE]', date)
    s = s.replace('[DO]', do)
    s = s.replace('[ADD]', add)
    s = s.replace('[ENTITY]', 'Q' + str(entity))
    if genre is not None:
        s += ' FILTER(?genre = wd:Q' + genre + ')'
    s += '} GROUP BY ?cat ?year order by ?date'
    #print(s)
    return s

def resultListEntity(cat,isBook,entity,do,genre):
    if isBook:
        date = 'P571'
    else:
        date = 'P577'
    try:
        sparql = createQuery(cat,date,entity,do,genre,'')
        results_df = SPARQL_reader.readSPARQL(sparql, "")
    except:
        time.sleep(60)
        results_df = SPARQL_reader.readSPARQL(sparql, "")
    return results_df


def resultListTwoEntity(cat,entity,entity2,do):
    secondEntity = '?cat wdt:' + do + ' wd:Q' + str(entity2) +'.'
    try:
        sparql = createQuery(cat,'P577',entity,do,'',secondEntity)
        results_df = SPARQL_reader.readSPARQL(sparql, "")
    except:
        time.sleep(60)
        results_df = SPARQL_reader.readSPARQL(sparql, "")
    return results_df


entities =  db.read_db('SELECT "EntityID", "Name", "isActor" FROM "Entities" where category like ' + "'person' " + ' order by "EntityID"')
start_year = 1987
end_year = 2007
step = 5
year_pairs = [(year, year + step) for year in range(start_year, end_year, step)]
year_pairs.append((start_year, end_year))

for entityid, entity, isActor in entities:
    for attrName, attrID, catName, catID in attributes:
        if catName == 'movies' and isActor == False:
            continue
        if catName == 'movies':
            additional = 'with a duration of more than 60 minutes'
                #('with a movie length of more than 60 minutes', 'P2047', '60')
        else:
            additional = ''

        #create question
        result = resultListEntity(catID, catName == 'book', entityid,attrID, None)
        if len(result) > 0:
            result['year.value'] = result['year.value'].astype(int)
            for pair in year_pairs:
                r = result[(result['year.value'] >= pair[0]) & (result['year.value'] <= pair[1])]
                answer = len(r)
                answerTime = len(r['year.value'].value_counts())

                if answer > 0:
                    #createGeneralQuestion(entityid, entity,attrName,pair[0],pair[1],additional,catName,'',answer,question_template_general,[8])
                    if pair[0] == start_year and pair[1] == end_year:
                        createGeneralQuestion(entityid, entity,attrName,pair[0],pair[1],additional,catName,'',answerTime,question_template_general_time,[8,9])


            if isActor and catName == 'movies':
                for genreName, genreID in genre:

                    #create questions
                    #print(result)
                    #print(result['genres.value'].str.contains(genreID).any())
                    if result['genres.value'].str.contains(genreID).any():

                        resultGenre = resultListEntity(catID, catName == 'book', entityid,attrID, genreID)
                        time.sleep(3)
                        if len(resultGenre) > 0:
                            #print(resultGenre['year.value'])

                            resultGenre['year.value'] = resultGenre['year.value'].astype(int)
                            print(resultGenre['year.value'])
                            for pair in year_pairs:
                                r = resultGenre[(resultGenre['year.value'] >= pair[0]) & (resultGenre['year.value'] <= pair[1])]
                                answer = len(r)
                                answerTime = len(r['year.value'].value_counts())
                                if answer > 0:
                                    #createGeneralQuestion(entityid, entity, attrName, pair[0],pair[1], additional, catName, genreName, answer,question_template_general,[8])
                                    if pair[0] == start_year and pair[1] == end_year:
                                        createGeneralQuestion(entityid, entity, attrName, pair[0],pair[1], additional, catName, genreName, answerTime,question_template_general_time,[8,9])

                entities2 = db.read_db(
                    'SELECT "EntityID", "Name" FROM "Entities" where "isActor" = true')

                coActorslist = getCoActors(entityid)
                if len(coActorslist) > 0:
                    coActorslist['date.value'] = pd.to_datetime(coActorslist['date.value'])

                    # Extract the year from the 'date.value' column
                    coActorslist['year'] = coActorslist['date.value'].dt.year

                    # Group by 'coActor' and 'year', and count the number of entries
                    result = coActorslist.groupby(['coActor.value', 'year']).size().reset_index(name='count')

                    for entityid2, entity2 in entities2:

                        if entityid != entityid2:

                            if (coActorslist == 'http://www.wikidata.org/entity/Q' + str(entityid2)).any().any():

                                #result = resultListTwoEntity(catID, entityid, entityid2, attrID)

                                for pair in year_pairs:
                                    #answer = len(result[(result['year.value'] >= pair[0]) & (result['year.value'] <= pair[1])])
                                    filtered_df = result[(result['coActor.value'] == 'http://www.wikidata.org/entity/Q' + str(entityid2)) & (result['year'] >= pair[0]) & (result['year'] <= pair[1])]
                                    # Calculate the sum of the 'count' column in the filtered DataFrame
                                    answerTime = len(filtered_df['year'].value_counts())
                                    answer = filtered_df['count'].sum()
                                    if answer > 0:
                                        #createActorQuestion(entityid, entity,entityid2, entity2,pair[0],pair[1],additional,answer,question_template_actor,[8])
                                        if pair[0] == start_year and pair[1] == end_year:
                                            createActorQuestion(entityid, entity,entityid2, entity2,pair[0],pair[1],additional,answerTime,question_template_actor_time,[8,9])







def extractQuestion(answer, id, properties,description):


    tmpQuestionTemplate = question_template_time.replace("[EVENT]", db.getNameOfEntity(id) + description)

    if answer is not None:
        json_data = '{"question": "' + tmpQuestionTemplate + '",' \
                                                             ' "answer": ' + json.dumps(answer) + ',' \
                                                                                                  ' "type": ' + json.dumps(
            str(1)) + '},'
        #print(json_data)
        db.write_answer([1], tmpQuestionTemplate, [answer], [id],None,[properties[0],properties[1]], None)

    return id, answer, properties, description

def createSparqlAndQuestion(qid, properties, threshold, isHigher):
    if isHigher:
        comperator = '>'
    else:
        comperator = '<'
    sparql = SPARQLGenerator2.SPARQLGeneratorCount(qid, properties, "FILTER ( ?var" + str(len(properties) -1) + " " + comperator + " " + str(threshold) +" )")
    results_df = SPARQL_reader.readSPARQL(sparql, "")
    return len(results_df)



