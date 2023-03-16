import logging
import os
import json

import azure.functions as func
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceNotFoundError
from schema import Schema, And


def main(req: func.HttpRequest) -> func.HttpResponse:
    pokemonName = req.route_params.get('pokemonName')

    bodyInput = {
        u'pokemonName': pokemonName,
    }

    schema = Schema({
         'pokemonName': And(str, len)
    })

    if not schema.is_valid(bodyInput):
        return func.HttpResponse("Invalid input types provided.", status_code=400)

    table_service_client  = TableServiceClient.from_connection_string(conn_str= os.environ["AzureWebJobsStorage"])
    table_client = table_service_client.get_table_client(table_name="Pokedex")

    try:
        entity = table_client.get_entity(pokemonName, pokemonName)
        bodyInput["pokemonNumber"] = entity["PokemonNumber"]
        bodyInput["pokemonType"] = entity["PokemonType"]
        bodyInput["pokemonColor"] = entity["PokemonColor"]
        bodyInput["pokemonAttacks"] = entity['PokemonAttacks'] if 'PokemonAttacks' in entity else []
        return func.HttpResponse(json.dumps(bodyInput))
    except ResourceNotFoundError as ex:
        logging.exception(ex)
        return func.HttpResponse("That pokemon doesn't exist.", status_code=404)