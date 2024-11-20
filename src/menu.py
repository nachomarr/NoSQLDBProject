import src.cassandra as cassandra
import src.mongo as mongo
import src.dgraph as dgraph

def loadData():
    cassandra.loadData()
    mongo.loadData()
    dgraph.loadData()
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
    ("Delete data", deleteData),
    ("Exit", None)
]

def runApp():
    selected = None
    while selected != len(MENU):
        printMenu()
        selected = input("Enter your choice: ")
        selected = int(selected) if selected.isdigit() else selected
        if isinstance(selected, int) and 1 <= selected < len(MENU):
            MENU[selected-1][1]()
        elif selected != len(MENU):
            print("Invalid option")
        print()

def printMenu():
    for i in range(len(MENU)):
        print(f"{i+1}. {MENU[i][0]}")