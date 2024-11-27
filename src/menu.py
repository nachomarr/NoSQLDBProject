import src.cassandra as cassandra
import src.mongo as mongo
import src.dgraph as dgraph
from src.login import Login

def loadData():
    cassandra.loadData()
    dgraph.loadData()
    mongo.loadData()
    print("Data loaded succesfully")

def deleteData():
    cassandra.deleteData()
    mongo.deleteData()
    dgraph.deleteData()
    print("Data deleted successfully")

MENU = [
    ("Load data", loadData),
    ("Get courses history", cassandra.getAllCourses),
    ("Find courses by date range", cassandra.getCoursesByDateRange),
    ("Find active courses", cassandra.getActiveCourses),
    ("Find courses by final grade", cassandra.getCoursesByFinalGrade),
    ("Get user data by email", mongo.getUserData),
    ("Get course details by ID", mongo.getCourseDetails),
    ("Search courses by title", mongo.searchCoursesByTitle),
    ("Search courses by instructor", mongo.searchCoursesByInstructor),
    ("Average Final Per Course", mongo.getAverageFinalGradePerCourse),
    ("View follows", dgraph.getFollows),
    ("View Likes and Dislikes from users",dgraph.getLikesandDislikes),
    ("View Recommended Courses",dgraph.recomendedCourses),
    ("Delete data", deleteData),
    ("Exit", None)
]

def runApp():
    user = Login()
    user.checklogin()
    selected = None
    while selected != len(MENU):
        printMenu()
        selected = input("Enter your choice: ")
        selected = int(selected) if selected.isdigit() else selected
        if isinstance(selected, int) and 1 <= selected < len(MENU):
            try:
                MENU[selected-1][1]()
            except:
                print("Something went wrong")
        elif selected != len(MENU):
            print("Invalid option")
        print()

def printMenu():
    for i in range(len(MENU)):
        print(f"{i+1}. {MENU[i][0]}")