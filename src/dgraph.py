import json
import pydgraph 
from src.databases import DBconnections
from src.login import Login
login = Login()
username = login.checklogin()["username"]

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
    name: string  @index(exact) @lang .
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
        print("Se creo el esquema de Dgraph :)")
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
    loadSchema(DBconnections.DGRAPH)
    
    for user in data.get("users"):
        obtainUser(user)
    for course in data.get("courses"):
        obtainCourse(course)

def getFollows():
    connection = DBconnections.DGRAPH

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
    
    username = input("Enter the name of the person you want to see their 👍 & 👎: ").strip()

    if not username:
        print("Error: You must enter a valid username.")
        return  

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


def printCourse(RCOURSE):
    connection = DBconnections.DGRAPH

    query = """
    query PrintCourses($name:string){
        PrintCourses(func:eq(name,$name)) {
            description
            registration_spaces
            keywords
            mode
        }
    }
    """
    variables = {"$name": RCOURSE}

    try:
        res = connection.txn(read_only=True).query(query, variables=variables)
        data = json.loads(res.json)
        if "PrintCourses" in data and len(data["PrintCourses"]) > 0:
            course_data = data["PrintCourses"][0]  # Assuming only one course is returned

            # Print the course data in a styled manner
            print(f"Course Information for: {RCOURSE}")
            print(f"Description: {course_data.get('description')}")
            print(f"Registration Spaces: {course_data.get('registration_spaces')}")
            print(f"Keywords: {course_data.get('keywords')}")
            print(f"Mode: {course_data.get('mode')}")
        else:
            print(f"No course found with the name '{RCOURSE}'.")
    except Exception as e:
        print(f"Error while querying Dgraph: {e}")
    print("----------------\n")


def FollowsCourse(FollowsOption):
    connection = DBconnections.DGRAPH
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
        likes {
            name
        }
      }
    }
    """

    variables = {"$name": FollowsOption}
    suscribed_courses_list = []
    liked_courses_list = []

    try:
        res = connection.txn(read_only=True).query(query, variables=variables)

        data = json.loads(res.json)

        if "FollowOption" in data and len(data["FollowOption"]) > 0:
            suscribed_courses = data["FollowOption"][0].get("suscribed", [])
            if suscribed_courses:
                for course in suscribed_courses:
                    suscribed_courses_list.append(course["name"])
            else:
                print(f"No courses found for user '{FollowsOption}'.")
            liked_courses = data["FollowOption"][0].get("likes", [])
            if liked_courses:
                for course in liked_courses:
                    liked_courses_list.append(course["name"])
            else:
                print(f"No liked courses found for user '{FollowsOption}'.")
            suscribed_names = set(suscribed_courses_list)
            liked_names = set(liked_courses_list)
            common_courses_names = list(suscribed_names.intersection(liked_names))
            
            for RCOURSE in common_courses_names:
                printCourse(RCOURSE)

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
