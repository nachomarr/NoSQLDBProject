import datetime
import json
import pydgraph 
from src.databases import DBconnections


def loadSchema(client):
    schema = """
    type user {
        c_uid
        name
        likes
        dislikes
        suscribed
        follows
        teaches
    }  

    type course {
        c_uid
        name
        description
        regristation_spaces
        keywords
        mode

    }

    c_uid: string @index(hash) .
    name: string  @index(exact).
    email: string .
    phone_number: string .
    likes: [uid] . 
    dislikes: [uid] .
    suscribed: [uid] .
    teaches: [uid] .  
    description: string .
    keywords: [string] .
    mode: string .
    regristation_spaces: int .
    follows: [uid] .
    """
    try:
        client.alter(pydgraph.Operation(schema=schema))
        print("Se creo el Esquema Dgraph :))")
    except Exception as e:
        print(f"Error en el esquema DGRAPH: {e}")

def obtainUser(user):
    id = user["id"]
    name = user["name"]
    likeList = []
    dislikeList = []
    suscribedList = []
    teachingList = []
    followsList = []

    for like in user["likes"]:
        likeList.append(like)
    
    for dislike in user["dislikes"]:
        dislikeList.append(dislike)
    
    for suscription in user["suscribed"]:
        suscribedList.append(suscription["course_id"])
    
    for teaching in user["teaches"]:
        teachingList.append(teaching)

    for follow in user["follows"]:
        followsList.append(follow)

    upload_user(id,name,likeList,dislikeList,suscribedList,teachingList,followsList)

def obtainCourse(course):
    id = course["id"]
    nameCourse = course["name"]
    descriptionCourse = course["description"]
    spaces = course["registration_spaces"]
    keywords = course["keywords"]
    mode = course["mode"]

    upload_course(id,nameCourse,descriptionCourse,spaces,keywords,mode)
    

def checkUID(uid):
    connection = DBconnections.DGRAPH

    query = """query id_exists($a: string){
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

def proccess_data(list,dgraph_type):
    proccessed_list = []
    for obj in list:
        obj_uid = checkUID(obj)
        if obj_uid is None:
            obj_uid = "_:new_obj_" + obj
        proccessed_list.append({"uid": obj_uid, "c_uid": obj, "dgraph.type": dgraph_type})

    return proccessed_list


def upload_user(id,name,likeList,dislikeList,suscribedList,teachingList,followsList):
    connection = DBconnections.DGRAPH
    txn = connection.txn()

    result = checkUID(id)

    if result is not None:
        user_uid = result
    else:
        user_uid = "_:new_obj"

    processed_likes = proccess_data(likeList,"course")
    processed_dislikes = proccess_data(dislikeList,"course")
    processed_suscribed = proccess_data(suscribedList,"course")
    proccessed_teaching = proccess_data(teachingList,"course")
    proccessed_follows = proccess_data(followsList,"user")
    
    try:
        user = {
            "uid":user_uid,
            "c_uid":id,
            "dgraph.type":"user",
            "name":name,
            "likes":processed_likes,
            "dislikes":processed_dislikes,
            "suscribed":processed_suscribed,
            "teaches":proccessed_teaching,
            "follows":proccessed_follows
        }

        txn.mutate(set_obj=user)
        
        txn.commit()
    except Exception as e:
        print(f"Error during creation of user: {e}")
    finally:
        txn.discard()

def upload_course(id,nameCourse,descriptionCourse,spaces,keywords,mode):
    connection = DBconnections.DGRAPH
    txn = connection.txn()

    result = checkUID(id)

    if result is not None:
        course_uid = result
    else:
        course_uid = "_:new_obj"
    try:
        course = {
            "uid":course_uid,
            "c_uid":id,
            "dgraph.type":"course",
            "name":nameCourse,
            "description":descriptionCourse,
            "registration_spaces":spaces,
            "keywords":keywords,
            "mode":mode
        }
        txn.mutate(set_obj=course)
        txn.commit()
    except Exception as e:
        print(f"Error during creation of course: {e}")
    finally:
        txn.discard()



def loadData():
    
    data = DBconnections.DATA
    
    for user in data.get("users"):
        obtainUser(user)
    for course in data.get("courses"):
        obtainCourse(course)


def deleteData():
    connection = DBconnections.DGRAPH
    return connection.alter(pydgraph.Operation(drop_all=True))