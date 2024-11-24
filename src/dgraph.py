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
        registration_spaces
        keywords
        mode
        start_date
        end_date
        

    }

    c_uid: string @index(exact) .
    name: string  @index(exact).
    likes: [uid] . 
    dislikes: [uid] .
    suscribed: [uid] .
    teaches: [uid] @reverse .  
    description: string .
    keywords: [string] .
    mode: string .
    registration_spaces: int .
    follows: [uid] .
    start_date: string .
    end_date: string .
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
    start_date = course["start_date"]
    end_date = course["end_date"]

    upload_course(id,nameCourse,descriptionCourse,spaces,keywords,mode,start_date,end_date)
    
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

def upload_course(id,nameCourse,descriptionCourse,spaces,keywords,mode,start_date,end_date):
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
            "mode":mode,
            "start_date":start_date,
            "end_date":end_date
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

def getFollows():
    connection = DBconnections.DGRAPH

    username = input("Enter your username: ")
    query = """query get_Follows($a: string) {
        all(func:eq(name,$a)){
        follows{
            name
        }
        }
    
    }
    """
    variable = {'$a':username}
    res = connection.txn(read_only=True).query(query, variables=variable)
    data = json.loads(res.json)

    if 'all' in data and len(data['all']) > 0:
        follows = data['all'][0].get('follows', [])
        print(f"{username} is following a total of {len(follows)} people")
        
        print(f"the names are: ")
        for follow in follows:
            print(" -",follow["name"])

    else:
        print(f"{username} is not following anyone.")

def getLikesandDislikes():
    connection = DBconnections.DGRAPH
    getFollows()
    
    # Prompt for the username (course name)
    username = input("Enter the name of the course you want to see their 👍 & 👎: ").strip()

    # Check if the username is empty
    if not username:
        print("Error: You must enter a valid course name.")
        return  # Exit the function early if no input is provided

    query = """
    query getLikesDislikes($a: string) {
        all(func:eq(name,$a)){
            likes {
                name
            }
            dislikes {
                name
            }
        }
    }
    """

    variable = {'$a': username}
    
    try:
        
        res = connection.txn(read_only=True).query(query, variables=variable)
        data = json.loads(res.json)

       
        if 'all' not in data or len(data['all']) == 0:
            print(f"No data found for course '{username}'.")
            return  
        
        likes = data['all'][0].get('likes', [])
        print(f"{username} likes a total of {len(likes)} courses")
        print("The names are: ")
        for like in likes:
            print(" -", like["name"])

        dislikes = data['all'][0].get('dislikes', [])
        print(f"\n{username} dislikes a total of {len(dislikes)} courses")
        print("The names are: ")
        for dislike in dislikes:
            print(" -", dislike["name"])

    except Exception as e:
        print(f"Error while querying Dgraph: {e}")


def getCurrentCourses():
    connection = DBconnections.DGRAPH
    username = input("Enter your username: ")
    query = """query getCurrentCourses($a: string) {
        all(func:eq(name,$a)){
        suscribed{
            name
            TeachedBy: ~teaches{
                name
                }
        }
        }
    
    }
    """

    variable = {'$a':username}
    res = connection.txn(read_only=True).query(query, variables=variable)
    data = json.loads(res.json)

    if 'all' in data and len(data['all']) > 0:
        user_data = data['all'][0]
        courses = user_data.get('suscribed', [])
        print(f"{username} is subscribed to {len(courses)} courses")
        
        print("The courses and their instructors are:")
        for course in courses:
            course_name = course.get("name", "Unknown Course")
            teachers = course.get("TeachedBy", [])
            
            print(f" - {course_name}")
            if teachers:
                print("Taught by:")
                for teacher in teachers:
                    print(f"     - {teacher.get('name', 'Unknown Teacher')}")
            else:
                print("   No instructors found for this course.")
    else:
        print(f"{username} is not subscribed to any courses.")

def ProfessorCourses(professor):
    connection = DBconnections.DGRAPH

    query = """
    query allTeachers($name: string) {
      allTeachers(func: eq(name, $name)) {
        teaches {
          name
          start_date
          end_date
          mode
          registration_spaces
        }
      }
    }
    """

    variables = {"$name":professor}
    res = connection.txn(read_only=True).query(query, variables=variables)
    data = json.loads(res.json)

    if "allTeachers" in data and len(data["allTeachers"]) > 0:
        teaches = data["allTeachers"][0].get("teaches", [])
        print(f"Courses taught by {professor}:")
        for course in teaches:
            print(f"- Name: {course['name']}")
            print(f"  Start Date: {course.get('start_date', 'N/A')}")
            print(f"  End Date: {course.get('end_date', 'N/A')}")
            print(f"  Mode: {course.get('mode', 'N/A')}")
            print(f"  Registration Spaces: {course.get('registration_spaces', 'N/A')}")
            print()
    else:
        print(f"No courses found for teacher '{professor}'.")

import json
import pydgraph

def FollowsCourse(FollowsOption):
    connection = DBconnections.DGRAPH  # Assuming this connects to Dgraph
    query = """
    query FollowOption($name: string) {
      FollowOption(func: eq(name, $name)) {
        suscribed {
          name
          start_date
          end_date
          mode
          registration_spaces
        }
      }
    }
    """

    # Set the variables for the query
    variables = {"$name": FollowsOption}

    try:
        # Execute the query in read-only mode
        res = connection.txn(read_only=True).query(query, variables=variables)

        # Parse the JSON response
        data = json.loads(res.json)

        # Check if the query returned any data
        if "FollowOption" in data and len(data["FollowOption"]) > 0:
            suscribed_courses = data["FollowOption"][0].get("suscribed", [])
            if suscribed_courses:
                print(f"Courses suscribed by {FollowsOption}:")
                for course in suscribed_courses:
                    print(f"- Name: {course['name']}")
                    print(f"  Start Date: {course.get('start_date', 'N/A')}")
                    print(f"  End Date: {course.get('end_date', 'N/A')}")
                    print(f"  Mode: {course.get('mode', 'N/A')}")
                    print(f"  Registration Spaces: {course.get('registration_spaces', 'N/A')}")
                    print()
            else:
                print(f"No courses found for user '{FollowsOption}'.")
        else:
            print(f"No such user found with the name '{FollowsOption}'.")

    except Exception as e:
        print(f"Error while querying Dgraph: {e}")




def recomendedCourses():

    print("View recomendation by \n 1. Current Professor? \n 2. Follows?")
    option = int(input("Choose 1 or 2: "))

    if option == 1:
        getCurrentCourses()
        print("\n")
        ProfessorOption = input("Choose the professor: ")
        print("---------------------------")
        ProfessorCourses(ProfessorOption)
        print("\n")
    elif option == 2:
        getFollows()
        FollowsOption = input("Choose the follower:")
        print("---------------------------")
        FollowsCourse(FollowsOption)
        print("\n")


def deleteData():
    connection = DBconnections.DGRAPH
    return connection.alter(pydgraph.Operation(drop_all=True))
