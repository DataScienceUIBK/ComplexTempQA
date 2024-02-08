import db
import json

print("[")

resultlist= []

def createJSON(query):
    result = db.read_db(query)
    for id, type, entity_q, entity_a, country_q, country_a, hop_p, time, question, answer, rating in result:

        if entity_q != None:
            for count, e in enumerate(entity_q):
                if e[1] == 'Q':
                    entity_q[count] = e[1:]
        if entity_a != None:
            for count, e in enumerate(entity_a):
                if e[1] == 'Q':
                    entity_a[count] = e[1:]
        if hop_p != None:
            for count, e in enumerate(hop_p):
                if e[1] == 'P':
                    hop_p[count] = e[1:]



        json_data = '{"question": "' + question + '",' \
                                ' "answer": ' + json.dumps(answer) + ',' \
                                ' "type": ' + json.dumps(type) + ','\
                                ' "entityQuestion": ' + json.dumps(entity_q) + ',' \
                                ' "entityAnswer": ' + json.dumps(entity_a) + ','\
                                ' "hopProperty": ' + json.dumps(hop_p) + \
                    '}'
        resultlist.append(json_data)


query = 'SELECT * FROM "Answer"'
createJSON(query)

prefix = ""
for j in resultlist:
    print(prefix + j)
    prefix = ','



print("]")