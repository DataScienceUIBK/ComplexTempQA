#!/usr/bin/python

import requests
import re
import time
import SPARQL_reader
import json
import sys

if len(sys.argv) == 1:
    print("need year for crawling")
    exit(2)


url = "https://en.wikipedia.org"
resp = requests.get(url + "/wiki/" + sys.argv[1])
sparqlQuery = 'SELECT DISTINCT ?superParent ?superParentLabel ?point ?start ?end WHERE {wd:[ENTITY] wdt:P31  ?parent. ?parent (wdt:P279*) ?superParent.OPTIONAL {wd:[ENTITY] wdt:P585 ?point}.OPTIONAL {wd:[ENTITY] wdt:P580 ?start}.OPTIONAL {wd:[ENTITY] wdt:P582 ?end}. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }}'


def listToString(list):
    result = "{"
    prefix = ""
    for item in list:
        result += prefix
        result += item

        prefix = ","
    return result + "}"


#print("ID;name;startDate;endDate;pointDate;country;instanceList")

if resp.status_code == 200:
    events = list()
    eventString = resp.text.partition('id="Events"')[2].partition('id="Births"')[0]
    eventUrls = re.findall('/wiki/\S+', eventString)
    for evUrl in eventUrls:
        evResp = requests.get(url + evUrl[:-1])
        if evResp.status_code == 200:
            wikidataURLRaw = re.findall("https://www.wikidata.org/wiki/Special:EntityPage/Q[0-9]+", evResp.text)
            if len(wikidataURLRaw) > 0:
                wikidataURL = wikidataURLRaw[0]
                dataResp = requests.get(wikidataURL.replace("Page", "Data") + ".json")
                wikiID = wikidataURL[49:]
                if dataResp.status_code == 200:
                    # 49 is the position after EntityPage/
                    dataJson = json.loads(dataResp.text)["entities"][wikiID]

                    start = ""
                    end = ""
                    point = ""
                    instanceList = None
                    if "P580" in dataJson["claims"]:
                        start = dataJson["claims"]["P580"][0]["mainsnak"]["datavalue"]["value"]["time"][1:11]
                    if "P582" in dataJson["claims"] and "datavalue" in dataJson["claims"]["P582"][0]["mainsnak"]:
                        end = dataJson["claims"]["P582"][0]["mainsnak"]["datavalue"]["value"]["time"][1:11]
                    if "P585" in dataJson["claims"] and "datavalue" in dataJson["claims"]["P585"][0]["mainsnak"]:
                        point = dataJson["claims"]["P585"][0]["mainsnak"]["datavalue"]["value"]["time"][1:11]
                    if "P31" in dataJson["claims"]:
                        instanceList = list()
                        for instance in dataJson["claims"]["P31"]:
                            instanceList.append(instance["mainsnak"]["datavalue"]["value"]["id"])

                    if (start != "" or end != "" or point != "") and instanceList is not None:
                        label = dataJson["labels"]["en"]["value"]
                        country = ""
                        if "P17" in dataJson["claims"]:
                            country = dataJson["claims"]["P17"][0]["mainsnak"]["datavalue"]["value"]["id"]
                        print(str(wikiID[1:]) + ";" + str(label.replace(";",
                                                                        ",")) + ";" + str(start) + ";" + str(
                            end) + ";" + str(point) + ";" + country + ";" + listToString(
                            instanceList))
                    #time.sleep(1)
