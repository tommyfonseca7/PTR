import logging
import os
import json

import azure.functions as func
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from schema import Schema, And, Use


def main(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()

    pokemonName = req.route_params.get('pokemonName')
    pokemonType = req_body.get('pokemonType')
    pokemonColor = req_body.get('pokemonColor')
    pokemonAttacks = req_body.get('pokemonAttacks')

    bodyInput = {
        u'pokemonName': pokemonName,
        u'pokemonType': pokemonType,
        u'pokemonColor': pokemonColor,
        u'pokemonAttacks': pokemonAttacks
    }

    schema = Schema({
         'pokemonName': And(str, len),
         'pokemonType': And(Use(str.lower), lambda s: s in ('normal','fire', 'water', 'grass', 'electric', 'ice', 'fighting', 'poison', 'flying', 'bug', 'psychic', 'ghost', 'dark', 'dragon')),
         'pokemonColor': And(Use(str.lower), lambda s: s in ('red', 'green' ,'blue', 'yellow', 'black', 'white', 'purple', 'orange', 'pink')),
         'pokemonAttacks': [str]
    })

    if not schema.is_valid(bodyInput):
        return func.HttpResponse("Invalid input types provided.", status_code=400)

    table_service_client  = TableServiceClient.from_connection_string(conn_str= os.environ["AzureWebJobsStorage"])
    table_client = table_service_client.get_table_client(table_name="Pokedex")

    try:
        entityToUpdate = table_client.get_entity(pokemonName, pokemonName)
        entityToUpdate["PokemonType"] = str.lower(pokemonType)
        entityToUpdate["PokemonColor"] = str.lower(pokemonColor)
        entityToUpdate["PokemonAttacks"] = str([str.lower(attack) for attack in pokemonAttacks])
        table_client.update_entity(entity=entityToUpdate)
        bodyInput["pokemonNumber"] = entityToUpdate["PokedexNumber"]
        return func.HttpResponse(json.dumps(bodyInput))
    except ResourceNotFoundError as ex:
        logging.exception(ex)
        return func.HttpResponse("That pokemon doesn't exist.", status_code=404)
    except ResourceExistsError as ex:
        logging.exception(ex)
        return func.HttpResponse("That pokemon already exists.", status_code=409)