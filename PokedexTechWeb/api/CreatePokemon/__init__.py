import logging
import os
import json

import azure.functions as func
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
from schema import Schema, And, Use

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    req_body = req.get_json()

    pokemonName = req_body.get('name')
    pokemonNumber = req_body.get('pokemonNumber')
    pokemonType = req_body.get('pokemonType')
    pokemonColor = req_body.get('pokemonColor')
    pokemonAttacks = req_body.get('pokemonAttacks')

    bodyInput = {
        u'pokemonName': pokemonName,
        u'pokemonNumber': pokemonNumber,
        u'pokemonType': pokemonType,
        u'pokemonColor': pokemonColor,
        u'pokemonAttacks': pokemonAttacks
    }

    schema = Schema({
         'pokemonName': And(str, len),
         'pokemonNumber': And(int),
         'pokemonType': And(Use(str.lower), lambda s: s in ('normal','fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison', 'flying', 'bug', 'psychic', 'ghost', 'dark', 'dragon')),
         'pokemonColor': And(Use(str.lower), lambda s: s in ('red', 'green' ,'blue', 'yellow', 'black', 'white', 'purple', 'orange', 'pink')),
         'pokemonAttacks': [str]
    })

    if not schema.is_valid(bodyInput):
        return func.HttpResponse("Invalid input types provided.", status_code=400)

    entityToInsert = {
        u'PartitionKey': pokemonName,
        u'RowKey': pokemonName,
        u'PokemonName': pokemonName,
        u'PokemonNumber': pokemonNumber,
        u'PokemonType': str.lower(pokemonType),
        u'PokemonColor': str.lower(pokemonColor),
        u'PokemonAttacks': str([str.lower(attack) for attack in pokemonAttacks])
    }

    table_service_client  = TableServiceClient.from_connection_string(conn_str= os.environ["AzureWebJobsStorage"])
    table_client = table_service_client.get_table_client(table_name="Pokedex")

    try:
        entityWithSamePokedexNumber = table_client.query_entities("PokemonNumber eq {}".format(entityToInsert['PokemonNumber']))
        if any(entityWithSamePokedexNumber):
            return func.HttpResponse("That pokemon already exists.", status_code=409)
        table_client.create_entity(entity=entityToInsert)
        return func.HttpResponse(json.dumps(bodyInput))
    except ResourceExistsError as ex:
        logging.exception(ex)
        return func.HttpResponse("That pokemon already exists.", status_code=409)