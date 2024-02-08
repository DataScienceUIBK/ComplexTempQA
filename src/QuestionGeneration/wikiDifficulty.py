#!/usr/bin/python

import db
import requests
import urllib.parse


viewLink = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/[NAME]/monthly/20150107/20221211"
headers = {
    'User-Agent': 'YOUR_APP_NAME (YOUR_EMAIL_OR_CONTACT_PAGE)'
}

def getPageView (id):
    link = 'https://www.wikidata.org/wiki/Special:EntityData/Q' + str(id) + '.json'
    tmpoutputEntity = requests.get(link).json().get('entities').get('Q' + str(id)).get('sitelinks')
    if 'enwiki' in tmpoutputEntity:
        outputEntity = tmpoutputEntity.get('enwiki').get('title')
        tmpLink = viewLink.replace('[NAME]', urllib.parse.quote(outputEntity))
        dataJson = requests.get(tmpLink, headers=headers).json()
        if 'items' in dataJson:
            sumView = 0
            for months in dataJson['items']:
                sumView += months['views']
            return sumView

    # else:
    # print("error in " + name)
    return None



#result = db.read_db('SELECT "EventID" FROM "Events"')
#for id in result:
#    sumView = getPageView(id[0])
#    if sumView is not None:
#        db.write_db('UPDATE "Events" SET "pageViews" = ' + str(sumView) + ' WHERE "EventID" = ' + str(id[0]))



#result = db.read_db('SELECT entity FROM "Input"')
#for entity in result:
#    sumView = getPageView(entity[0])
#    if sumView is not None:
#        db.write_db('UPDATE "Input" SET "pageViews" = ' + str(sumView) + ' WHERE entity = ' + str(entity[0]))


result = db.read_db('SELECT "EntityID" FROM "Entities" WHERE "pageViews" is Null ORDER BY "EntityID" ASC ')
for entity in result:
    print(entity[0])
    sumView = getPageView(entity[0])
    if sumView is not None:
        db.write_db('UPDATE "Entities" SET "pageViews" = ' + str(sumView) + ' WHERE "EntityID" = ' + str(entity[0]))