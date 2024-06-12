import db
import requests
import json
import re
from datetime import datetime

# Define question templates
questionTemplateCountry = "In which country did the [EVENT] happen?"
questionTemplateCountryYesNo = "Did the [EVENT] happen in [COUNTRY]?"
questionTemplateDate = "When was the [EVENT]?"
questionTemplateSignal = "Did [EVENT1] happen [SIGNAL] [EVENT2]?"
questionTemplateFirst = "Did [EVENT1] or [EVENT2] happen first?"
questionTemplateTripleFirst = "Which one happened first, [EVENT1], [EVENT2], or [EVENT3]?"
questionAttributeInt = "What was [ATTR] of [EVENT]?"
questionAttributePerson = "Who was [ATTR] of [EVENT]?"
questionAttributeComp = "Did the [EVENT1] have a [COMPARE] [ATTR] than the [EVENT2]?"
questionAttributeCompEv = "Did [EVENT1] or [EVENT2] have a [COMPARE] [ATTR]?"
questionAttributeTripleComp = "[EVENT1], [EVENT2], or [EVENT3], which one had a [COMPARE] [ATTR]?"

# Function to create a before/after question
def createBeforeAfterQuestion(eventid1, event1, eventid2, event2, signal, answer):
    answerString = "yes" if answer else "no"
    tmpQuestionTemplate = questionTemplateSignal.replace("[EVENT1]", event1).replace("[EVENT2]", event2).replace("[SIGNAL]", signal)
    db.write_answer([4], tmpQuestionTemplate, [answerString], [str(eventid1), str(eventid2)], None, None, None)

# Function to create a question about which event happened first
def createHappenFirstQuestion(eventid1, event1, eventid2, event2, isFirstEvent):
    answer = event1 if isFirstEvent else event2
    answerid = eventid1 if isFirstEvent else eventid2
    tmpQuestionTemplate = questionTemplateFirst.replace("[EVENT1]", event1).replace("[EVENT2]", event2)
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1), str(eventid2)], [str(answerid)], None, None)

# Function to create a question about which event happened first among three events
def createHappenFirstQuestionTriple(eventid1, event1, eventid2, event2, event3, answerEvent):
    tmpQuestionTemplate = questionTemplateTripleFirst.replace("[EVENT1]", event1).replace("[EVENT2]", event2).replace("[EVENT3]", event3)
    return json.dumps({"question": tmpQuestionTemplate, "answer": answerEvent, "type": 4})

# Function to create a question about an attribute of an event
def createAttributeQuestion(eventid, event, attr, answer):
    tmpQuestionTemplate = questionAttributeInt.replace("[EVENT]", event).replace("[ATTR]", attr)
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid)], None, None, None)

# Function to create a question about a person-related attribute of an event
def createAttributePersonQuestion(eventid, event, attr, answer, answerid):
    tmpQuestionTemplate = questionAttributePerson.replace("[EVENT]", event).replace("[ATTR]", attr)
    db.write_answer([4], tmpQuestionTemplate, answer, [str(eventid)], answerid, None, None)

# Function to create a comparison question between two events
def createAttrCompQuestion(eventid1, event1, eventid2, event2, compr, attr, isFirstEvent):
    answer = "yes" if isFirstEvent else "no"
    tmpQuestionTemplate = questionAttributeComp.replace("[EVENT1]", event1).replace("[EVENT2]", event2).replace("[COMPARE]", compr).replace("[ATTR]", attr)
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1), str(eventid2)], None, None, None)

# Function to create a comparison question about which event has a higher attribute value
def createAttrCompQuestionEv(eventid1, event1, eventid2, event2, compr, attr, isFirstEvent):
    answer = event1 if isFirstEvent else event2
    answerid = eventid1 if isFirstEvent else eventid2
    tmpQuestionTemplate = questionAttributeCompEv.replace("[EVENT1]", event1).replace("[EVENT2]", event2).replace("[COMPARE]", compr).replace("[ATTR]", attr)
    db.write_answer([4], tmpQuestionTemplate, [answer], [str(eventid1), str(eventid2)], [str(answerid)], None, None)

# Function to create a comparison question among three events
def createAttrCompQuestionTriple(eventid1, event1, eventid2, event2, event3, attr, answerEvent):
    tmpQuestionTemplate = questionAttributeTripleComp.replace("[EVENT1]", event1).replace("[EVENT2]", event2).replace("[EVENT3]", event3).replace("[ATTR]", attr)
    return json.dumps({"question": tmpQuestionTemplate, "answer": answerEvent, "type": 4})

# Process event attributes and create questions based on them
def process_event_attributes(eventId, eventName, numberAttributes):
    attributes = [
        (numberAttributes[1], "the number of deaths"),
        (numberAttributes[2], "the number of injured people"),
        (numberAttributes[3], "the number of survivors"),
        (numberAttributes[4], "the number of participants"),
        (numberAttributes[5], "maximum sustained wind in m/s"),
        (numberAttributes[6], "lowest atmospheric pressure in hectopascal"),
        (numberAttributes[7], "total number of ballots cast"),
        (numberAttributes[8], "number of eligible voters"),
        (numberAttributes[9], "number of attendees"),
        (numberAttributes[10], "number of valid votes"),
        (numberAttributes[11], "earthquake magnitude on the Richter magnitude scale"),
        (numberAttributes[12], "vertical depth"),
        (numberAttributes[13], "number of games played"),
        (numberAttributes[14], "number of points scored"),
        (numberAttributes[15], "number of perpetrators"),
        (numberAttributes[16], "number of negative votes"),
        (numberAttributes[17], "number of support votes")
    ]

    for attribute_value, attribute_name in attributes:
        if attribute_value > -1:
            createAttributeQuestion(eventId, eventName, attribute_name, attribute_value)

# Example function calls for testing
print("[")

numberAttributes = db.readAttributeEvents()

for eventId, *attributes in numberAttributes:
    event = db.read_event(eventId)
    if event:
        eventName = event[0][0]
        if event[0][1]:
            eventName += f" {event[0][1]}"
        process_event_attributes(eventId, eventName, attributes)

print("]")
