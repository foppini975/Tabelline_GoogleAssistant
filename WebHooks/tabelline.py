import logging
import json
import pdb
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api

import dyncontest

"""
https://medium.com/@manivannan_data/how-to-deploy-the-flask-app-as-ubuntu-service-399c0adf3606
"""

"""
Restart and show logs:

sudo systemctl restart tabelline.service; sudo journalctl -f -u tabelline

"""

app = Flask(__name__)
api = Api(app)

logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.WARNING)


class Tabelline(Resource):
    def post(self):
        json_data = request.json
        responseId = json_data['responseId']
        intentName = json_data['queryResult']['intent']['displayName']
        app.logger.info("-------- NEW REQUEST --------")
        app.logger.info("responseId: {} - intent: {}".format(responseId, intentName))
        app.logger.info("data: {}".format(json.dumps(json_data)))
        unrecognized_string = "Non ho capito"

        fullfillmentJson = { "fulfillmentMessages": [{"text": { "text": [ unrecognized_string ] }}],
                "fulfillmentText": "Unrecognized intent",
                "payload": {
                "google": {
                "expectUserResponse": True,
                "richResponse": {"items": [{"simpleResponse": {"textToSpeech": unrecognized_string}}]}
                }
                },
        }
        if intentName in ["richiestaTabellina", "richiestaTabellinaFinoA", "richiestaTutteTabelline", "rispostaNumero", "statistiche"]:
                # richiesta di un nuovo tipo di domande
                # (singola tabellina, fino a una certa tabellina, tutte le tabelline)
                dc = dyncontest.DynContest(json_data, logging.getLogger())
                return make_response(jsonify(dc.respond()))

        resp = jsonify(fullfillmentJson)
        resp.status_code = 200
        return resp

api.add_resource(Tabelline, '/tabelline') 

if __name__ == '__main__':
     PORT = 5004
     print("Listening on port {}...".format(PORT))
     app.run(port='{}'.format(PORT))

