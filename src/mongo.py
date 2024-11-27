import json
from src.databases import DBconnections

def createIndexes():
    
    DBconnections.MONGO['users'].create_index('email', unique=True)
    DBconnections.MONGO['courses'].create_index('instructor_id')


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


def paginateResults(results, page_size=5, format_func=lambda x: x):

    index = 0
    while index < len(results):
        for res in results[index:index + page_size]:
            print(format_func(res))
        index += page_size
        if index < len(results):
            user_input = input("Press Enter to see more results or any other key to quit: ")
            if user_input.lower() != '':
                break


def getUserData():
    email = input("Enter user's email: ")
    user = DBconnections.MONGO['users'].find_one({'email': email})
    if user:
        print("User Details:")
        print(f"Name: {user.get('name', 'N/A')}")
        print(f"Email: {user.get('email', 'N/A')}")
        print(f"Phone Number: {user.get('phone_number', 'N/A')}")
        
        follows = user.get('follows', [])
        if follows:
            print(f"Follows ({len(follows)} users):")
            for user_id in follows[:3]:
                followed_user = DBconnections.MONGO['users'].find_one({'id': user_id})
                if followed_user:
                    print(f"  - Name: {followed_user.get('name', 'N/A')} (ID: {user_id})")
            if len(follows) > 3:
                print(f"  ... and {len(follows) - 3} more")
        else:
            print("Follows: None")
        
        likes = user.get('likes', [])
        if likes:
            print(f"Likes ({len(likes)} courses):")
            for course_id in likes[:3]:
                liked_course = DBconnections.MONGO['courses'].find_one({'id': course_id})
                if liked_course:
                    print(f"  - Name: {liked_course.get('name', 'N/A')} (ID: {course_id})")
            if len(likes) > 3:
                print(f"  ... and {len(likes) - 3} more")
        else:
            print("Likes: None")
        
        dislikes = user.get('dislikes', [])
        print(f"Dislikes: {len(dislikes)} courses" if dislikes else "Dislikes: None")
        
        subscribed_courses = user.get('suscribed', [])
        if subscribed_courses:
            print(f"Subscribed Courses ({len(subscribed_courses)}):")
            for sub in subscribed_courses[:3]:
                course = DBconnections.MONGO['courses'].find_one({'id': sub['course_id']})
                if course:
                    print(f"  - Name: {course.get('name', 'N/A')} (ID: {sub['course_id']})")
            if len(subscribed_courses) > 3:
                print(f"  ... and {len(subscribed_courses) - 3} more")
        else:
            print("Subscribed Courses: None")
        
        teaches = user.get('teaches', [])
        print(f"Teaches: {len(teaches)} courses" if teaches else "Teaches: None")
    else:
        print("User not found")

def getCourseDetails():
    course_id = input("Enter course ID: ")
    course = DBconnections.MONGO['courses'].find_one({'id': course_id})
    if course:
        print("Course Details:")
        print(f"Name: {course.get('name', 'N/A')}")
        print(f"Description: {course.get('description', 'N/A')}")
        print(f"Start Date: {course.get('start_date', 'N/A')}")
        print(f"End Date: {course.get('end_date', 'N/A')}")
        print(f"Instructor ID: {course.get('instructor_id', 'N/A')}")
        print(f"Registration Spaces: {course.get('registration_spaces', 'N/A')}")
        keywords = course.get('keywords', [])
        print(f"Keywords: {', '.join(keywords) if keywords else 'None'}")
        print(f"Mode: {course.get('mode', 'N/A')}")
    else:
        print("Course not found")


def searchCoursesByTitle():
    title = input("Enter course title: ")
    courses = list(DBconnections.MONGO['courses'].find({'name': {'$regex': title, '$options': 'i'}}).sort('average_grade')) 
    if courses:
        print(f"Found {len(courses)} course(s) matching the title '{title}':")
        paginateResults(
            courses, 
            format_func=lambda x: f"  - Name: {x.get('name', 'N/A')} (ID: {x.get('id', 'N/A')})"
        )
    else:
        print("No courses found with that title")


def searchCoursesByInstructor():
    instructor_name = input("Enter instructor name: ")
    instructor = DBconnections.MONGO['users'].find_one({'name': {'$regex': instructor_name, '$options': 'i'}})
    if instructor:
        instructor_id = instructor['id']
        courses = list(DBconnections.MONGO['courses'].find({'instructor_id': instructor_id}))
        if courses:
            print(f"Found {len(courses)} course(s) taught by '{instructor_name}':")
            for course in courses[:3]:  # Mostrar solo los primeros 3 cursos
                print(f"  - Name: {course.get('name', 'N/A')} (ID: {course.get('id', 'N/A')})")
            if len(courses) > 3:
                print(f"  ... and {len(courses) - 3} more")
        else:
            print("No courses found for that instructor")
    else:
        print("Instructor not found")



def getAverageFinalGradePerCourse():

    pipeline = [
        {
            '$unwind': '$suscribed'
        },
        {
            '$group': {
                '_id': '$suscribed.course_id',
                'average_grade': {'$avg': '$suscribed.final_grade'}
            }
        },
        {
            '$lookup': {
                'from': 'courses',
                'localField': '_id',
                'foreignField': 'id',
                'as': 'course_details'
            }
        },
        {
            '$unwind': '$course_details'
        },
        {
            '$project': {
                'course_name': '$course_details.name',
                'course_id': '$_id',
                'average_grade': 1
            }
        }
    ]
    result = list(DBconnections.MONGO['users'].aggregate(pipeline))
    if result:
        paginateResults(
            result, 
            format_func=lambda x: f"Course Name: {x.get('course_name', 'N/A')}, Course ID: {x.get('course_id', 'N/A')}, Average Final Grade: {x.get('average_grade', 0):.2f}"
        )
    else:
        print("No data available for average final grades.")