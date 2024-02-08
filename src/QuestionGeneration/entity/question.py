import random
import db
from datetime import datetime  # Add this import

def set_to_empty_string_if_none(variable):
    if variable is None:
        return ""
    return variable


class Question:
    def __init__(self, is_event, entity1, answer, type, answer_entity_id=None, timeframe=None, unnamed=None, entity2=None, entity3=None, input_country=None, output_country=None):
        self.entity1 = entity1                          # (qid, name)
        self.answer = answer                            # [text]
        self.type = type                                # [int]
        self.timeframe = timeframe                      # [dates]
        self.unnamed = unnamed                          # [qid]
        self.answer_entity_id = answer_entity_id        # [qid]
        self.entity2 = entity2                          # (qid, name)
        self.entity3 = entity3                          # (qid, name)
        self.input_country = input_country
        self.output_country = output_country
        self.is_event = is_event

    def setAnswer(self, anwser):
        self.answer = anwser

    def setInput_country(self, input_country):
        self.input_country = input_country

    def setOutput_country(self, output_country):
        self.output_country = output_country

    def setAnswerEntity_id(self, answer_entity_id):
        self.answer_entity_id = answer_entity_id

    def getPlaceholder(self, number=None):
        if number is None:
            if self.is_event:
                return "[EVENT]"
            else:
                return "[ENTITY]"
        else:
            if self.is_event:
                return "[EVENT" + str(number) +"]"
            else:
                return "[ENTITY" + str(number) +"]"

    def spinnEntitites(self):
        # Create a list of non-None entities
        entities = [entity for entity in [self.entity1, self.entity2, self.entity3] if entity is not None]

        # Shuffle the entities randomly
        random.seed(3241235)
        random.shuffle(entities)

        # Update the entities in the question
        self.entity1 = entities[0] if self.entity1 is not None else None
        self.entity2 = entities[1] if self.entity2 is not None else None
        self.entity3 = entities[2] if self.entity3 is not None else None

    def getQuestionEntities(self):
        result = list()
        result.append(self.entity1[0])
        if self.entity2 is not None:
            result.append(self.entity2[0])
        if self.entity3 is not None:
            result.append(self.entity3[0])
        return result

    def createQuestion(self, questionTemplate, verb=None, signal=None,compare=None,attr=None,action=None,country=None, time=None,w=None,spinnable=False):
        verb = set_to_empty_string_if_none(verb)
        signal = set_to_empty_string_if_none(signal)
        compare = set_to_empty_string_if_none(compare)
        attr = set_to_empty_string_if_none(attr)
        action = set_to_empty_string_if_none(action)
        time = set_to_empty_string_if_none(time)
        country = set_to_empty_string_if_none(country)
        w = set_to_empty_string_if_none(w)

        if self.timeframe is not None and type(self.timeframe[0]) == str:
            self.timeframe = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in self.timeframe]

        if self.entity3 is None:
            if self.entity2 is None:
                self.create1Question( questionTemplate, verb, signal,compare,attr,action,country,w,time)
            else:
                self.create2Question( questionTemplate, verb, signal,compare,attr,action,country,w,time,spinnable)
        else:
            self.create3Question(questionTemplate, verb, signal, compare, attr,action,country,w,time,spinnable)

    def create1Question(self, questionTemplate, verb, signal,compare,attr,action,country, w,time):
        tmpQuestionTemplate = questionTemplate.replace(self.getPlaceholder(), self.entity1[1])
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[V]", verb)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[W]", w)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compare)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[TIME]',  time)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[ACTION]',  action)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[COUNTRY]',  country)

        #print(tmpQuestionTemplate +  str(self.answer))
        #db.write_answer(self.type, tmpQuestionTemplate, self.answer, ['Q' + str(self.entity1[0]), 'Q' + str(self.entity2[0])], None,None, None)
        db.write_answer2(self,tmpQuestionTemplate)


    def create2Question(self, questionTemplate, verb, signal,compare,attr,action,country, time, w,spinnable=False):
        if spinnable:
            self.spinnEntitites()
        tmpQuestionTemplate = questionTemplate.replace(self.getPlaceholder(1), self.entity1[1])
        tmpQuestionTemplate = tmpQuestionTemplate.replace(self.getPlaceholder(2), self.entity2[1])
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[V]", verb)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[W]", w)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compare)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[TIME]',  time)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[ACTION]',  action)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[COUNTRY]',  country)

        #print(tmpQuestionTemplate +  str(self.answer))
        #db.write_answer(self.type, tmpQuestionTemplate, self.answer, ['Q' + str(self.entity1[0]), 'Q' + str(self.entity2[0])], None,None, None)
        db.write_answer2(self,tmpQuestionTemplate)

    def create3Question(self, questionTemplate, verb, signal,compare,attr,action,country, time,w,spinnable=False):
        if spinnable:
            self.spinnEntitites()
        tmpQuestionTemplate = questionTemplate.replace(self.getPlaceholder(1), self.entity1[1])
        tmpQuestionTemplate = tmpQuestionTemplate.replace(self.getPlaceholder(2), self.entity2[1])
        tmpQuestionTemplate = tmpQuestionTemplate.replace(self.getPlaceholder(3), self.entity3[1])
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[SIGNAL]", signal)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[V]", verb)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[W]", w)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[COMPARE]", compare)
        tmpQuestionTemplate = tmpQuestionTemplate.replace("[ATTR]", attr)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[TIME]',  time)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[ACTION]',  action)
        tmpQuestionTemplate = tmpQuestionTemplate.replace('[COUNTRY]',  country)

        #print(tmpQuestionTemplate +  str(self.answer))
        #db.write_answer(self.type, tmpQuestionTemplate, self.answer, ['Q' + str(self.entity1[0]), 'Q' + str(self.entity2[0])], None,None, None)
        db.write_answer2(self,tmpQuestionTemplate)
