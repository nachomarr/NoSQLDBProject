import datetime
import json
import pydgraph 
from src.databases import DBconnections


def loadSchema(client):
    schema = """
    type user {
        c_uid
        name
        email
        phone_number
        likes
        dislikes
        suscribed
        teaches
    }  

    type course {
        c_uid
        name
        description
        start_date
        end_date
        regristation_spaces
        keywords
        mode

    }

    c_uid: string @index(exact) .
    name: string .
    email: string .
    phone_number: string .
    likes: [uid] . 
    dislikes: [uid] .
    suscribed: [uid] .
    teaches: [uid] .  
    description: string .
    start_date: datetime .
    end_date: datetime .
    keywords: [string] .
    mode: string .
    regristation_spaces: int .
    """
    try:
        client.alter(pydgraph.Operation(schema=schema))
        print("Se creo el Esquema Dgraph :))")
    except Exception as e:
        print(f"Error en el esquema DGRAPH: {e}")

def loadData():
    connection = DBconnections.DGRAPH
    data = DBconnections.DATA
    i = 0
    for user in data.get("users"):
        print(user['follows'])
        i+=1

    print(i)
def deleteData():
    pass