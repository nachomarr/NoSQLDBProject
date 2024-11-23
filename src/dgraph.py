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

def obtainUser(user):
    id = user["id"]
    name = user["name"]
    email = user["email"]
    phone = user["phone_number"]
    likeList = []
    for like in user["likes"]:
        likeList.append(like)

    upload_user(id,name,email,phone,likeList)

def checkUID(uid):
    connection = DBconnections.DGRAPH

    query = """query user_exists($a: string){
        all(func: eq(c_uid,$a)){
        uid
        }
    }
    """

    variables = {'$a': uid}
    res = connection.txn(read_only=True).query(query, variables=variables)
    user = json.loads(res.json)

    if "all" in user and len(user["all"]) > 0:
        return user["all"][0]["uid"]
    else:
        return None 

def upload_user(id,name,email,phone,likeList):
    connection = DBconnections.DGRAPH
    txn = connection.txn()

    result = checkUID(id)

    if result is not None:
        user_uid = result
    else:
        user_uid = "_:new_obj"

    processed_likes = []
    for like in likeList:
        course_uid = checkUID(like)
        if course_uid is None:
            course_uid = "_:course_" + like  # Create a blank node for a new course
        processed_likes.append({"uid": course_uid, "c_uid": like, "dgraph.type": "course"})

    try:

        user = {
            "uid":user_uid,
            "c_uid":id,
            "dgraph.type":"user",
            "name":name,
            "email":email,
            "phone_number":phone,
            "likes":processed_likes
        }

        txn.mutate(set_obj=user)

        commit_response = txn.commit()
        print(f"Commit Response: {commit_response}")
    except Exception as e:
        print(f"Error during upsert: {e}")
    finally:
        txn.discard()



def loadData():
    
    data = DBconnections.DATA
    
    for user in data.get("users"):
        obtainUser(user)


def deleteData():
    connection = DBconnections.DGRAPH
    return connection.alter(pydgraph.Operation(drop_all=True))