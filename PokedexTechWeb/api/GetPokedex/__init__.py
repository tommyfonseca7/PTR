import logging
import os
import json

import azure.functions as func
from azure.data.tables import TableServiceClient


def main(req: func.HttpRequest) -> func.HttpResponse:

    table_service_client  = TableServiceClient.from_connection_string(conn_str= os.environ["AzureWebJobsStorage"])
    table_client = table_service_client.get_table_client(table_name="Pokedex")
    entities = table_client.list_entities()
    pokedex = []
    for entity in entities:
       pokedex.append({
        'PokemonName': entity['PokemonName'],
        'PokemonNumber': entity['PokemonNumber'],
        'PokemonType': entity['PokemonType'],
        'PokemonColor': entity['PokemonColor'],
        'PokemonAttacks': entity['PokemonAttacks'] if 'PokemonAttacks' in entity else []
       })

    return func.HttpResponse(json.dumps(pokedex))
