# import the JSON utility package since we will be working with a JSON object
import json
import os
import random
from datetime import datetime

class DynContest:

    def __init__(self, json_data, logger = None):
        self.json_data = json_data
        self.session = self.json_data['session']
        self.responseId = self.json_data['responseId']
        self.queryText = self.json_data['queryResult']['queryText']
        self.intentName = self.json_data['queryResult']['intent']['displayName']
        self.logger = logger
        random.seed(datetime.now())

    def getContextParameters(self, context):
        try:
            contexts = self.json_data["queryResult"]["outputContexts"]
        except KeyError:
            return {}
        context_name = os.path.join(self.session, "contexts", context)
        self.logger.info("outputContexts: {}".format(json.dumps(contexts)))
        try:
            parameters = [c['parameters'] for c in contexts if c['name'] == context_name][0]
        except KeyError:
            parameters = {}
        return parameters

    def generateResponse(self, response_string, context, context_params = None):
        fulFillmentMessages = { "fulfillmentMessages": [
                { "text": { "text": [ response_string ] } }
            ],
            "fulfillmentText": response_string,
            "payload": {
                "google": {
                  "expectUserResponse": True,
                  "richResponse": { "items": [{ "simpleResponse": {"textToSpeech": response_string}}]}
                }
              }
        }
        if context_params is not None:
            fulFillmentMessages["outputContexts"] = [
                {
                  "name": os.path.join(self.session, "contexts", context),
                  "lifespanCount": 5,
                  "parameters": context_params
                }
            ]
        return fulFillmentMessages

    def getRandomCongrats(self):
        congrats = ['Bravo!', 'Ottimo!', 'Eccezionale!', 'Esatto!', 'Fortissimo!']
        r = random.randint(0, len(congrats) - 1)
        return congrats[r]

    def calcolaVoto(self, ratio):
        voti_dict = { .6: "Il tuo voto è 6", .65: "Il tuo voto è 6 e mezzo",
                        .7: "Il tuo voto è 7", .75: "Il tuo voto è 7 e mezzo",
                        .8: "Il tuo voto è 8", .85: "Il tuo voto è 8 e mezzo",
                        .9: "Il tuo voto è 7", .95: "Il tuo voto è 9 e mezzo",
                        1: "Il tuo voto è 10!" }
        key_list = list(voti_dict.keys())
        key_list.sort(reverse=True)
        for key in key_list:
            if ratio >= key:
                return voti_dict[key]
        return "Studia di più..."

    def respond(self):
        context_name = "question-context"
        parameters = self.getContextParameters(context_name)
        self.logger.info("Context parameters: {}".format(parameters))

        if 'score' not in parameters:
            parameters['score'] = 0
        if 'length' not in parameters:
            parameters['length'] = 0

        lastQuestionFeedback = ""
        if self.intentName == "richiestaTabellina":
            parameters['allowed'] = [int(parameters['tNum'])]
        elif self.intentName == "richiestaTabellinaFinoA":
            parameters['allowed'] = list(range(2, 1 + int(parameters['tNum'])))
        elif self.intentName == "richiestaTutteTabelline":
            parameters['allowed'] = list(range(2,11))
        elif self.intentName == "rispostaNumero":
            risultatoUtente = parameters['number-integer']
            risultatoAtteso = parameters['last_question']['first_number'] * parameters['last_question']['second_number']
            if risultatoUtente == risultatoAtteso:
                lastQuestionFeedback = self.getRandomCongrats()
                parameters['score'] += 1
            else:
                lastQuestionFeedback = "Attento! {:.0f} per {:.0f} fa {:.0f}. Ora dimmi ".format(parameters['last_question']['first_number'], parameters['last_question']['second_number'], risultatoAtteso)
            parameters['length'] += 1
        elif self.intentName == "statistiche":
            score = parameters['score']
            length = parameters['length']
            lastQuestionFeedback = "Hai risposto correttamente a {:.0f} domande su {:.0f}. {}. Ora dimmi ".format(score, length, self.calcolaVoto(score/length))

        first_number = random.randrange(max(2, min(parameters['allowed'])), 1 + min(max(parameters['allowed']), 10))
        second_number = random.randrange(2, 11)

        parameters['last_question'] = { 'first_number': first_number,
            'second_number': second_number }

        response_string = "{} {} per {}".format(lastQuestionFeedback, first_number, second_number)

        self.logger.info("{} - allowed: {} - response: {} - score: {}/{}".format(self.intentName, parameters['allowed'], response_string, parameters['score'], parameters['length']))

        fulfillmentJson = self.generateResponse(response_string, context_name, parameters)        
        return fulfillmentJson
        """
        result = {
            'statusCode': 200,
            'body': json.dumps(fulfillmentJson),
        }
        self.logger.info("##### Result")
        self.logger.info(result)
        return result
        """