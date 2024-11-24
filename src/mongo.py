import json
from src.databases import DBconnections

def loadData():
    try:
        with open("data/dataset.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: dataset.json no encontrado. Genera el dataset antes de cargar los datos.")
        return

    if 'users' in data:
        users = data['users']
        if isinstance(users, list):
            DBconnections.MONGO['users'].insert_many(users)
        else:
            print("Error en el formato de datos: 'users' debe ser una lista.")

    if 'courses' in data:
        courses = data['courses']
        if isinstance(courses, list):
            DBconnections.MONGO['courses'].insert_many(courses)
        else:
            print("Error en el formato de datos: 'courses' debe ser una lista.")

def deleteData():
    DBconnections.MONGO['users'].delete_many({})
    DBconnections.MONGO['courses'].delete_many({})

def getUserData():
    email = input("Enter user's email: ")
    user = DBconnections.MONGO['users'].find_one({'email': email})
    if user:
        user = (
            f"User:\n"
            f"Name: {user.get('name', 'N/A')}\n"
            f"Email: {user.get('email', 'N/A')}\n"
            f"Phone Number: {user.get('phone_number', 'N/A')}\n"
            f"Follows: {', '.join(user.get('follows', [])) if user.get('follows') else 'None'}\n"
            f"Likes: {', '.join(user.get('likes', [])) if user.get('likes') else 'None'}\n"
            f"Dislikes: {', '.join(user.get('dislikes', [])) if user.get('dislikes') else 'None'}\n"
            f"Subscribed Courses: {', '.join([sub['course_id'] for sub in user.get('suscribed', [])]) if user.get('suscribed') else 'None'}\n"
            f"Teaches: {', '.join(user.get('teaches', [])) if user.get('teaches') else 'None'}"
        )
        print(user)
    else:
        print("User not found")

def getCourseDetails():
    course_id = input("Enter course ID: ")
    course = DBconnections.MONGO['courses'].find_one({'id': course_id}) 
    print(course if course else "Course not found")

def searchCoursesByTitle():
    title = input("Enter course title: ")
    courses = list(DBconnections.MONGO['courses'].find({'name': {'$regex': title, '$options': 'i'}})) 
    if courses:
        for course in courses:
            print(course)
    else:
        print("No courses found with that title")

def searchCoursesByInstructor():
    instructor_name = input("Enter instructor name: ")
    instructor = DBconnections.MONGO['users'].find_one({'name': {'$regex': instructor_name, '$options': 'i'}})
    if instructor:
        instructor_id = instructor['id']
        courses = list(DBconnections.MONGO['courses'].find({'instructor_id': instructor_id}))
        if courses:
            for course in courses:
                print(course)
        else:
            print("No courses found for that instructor")
    else:
        print("Instructor not found")
