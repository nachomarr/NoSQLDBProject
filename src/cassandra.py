import os
import datetime
from src.databases import DBconnections

KEYSPACE_NAME = os.getenv('CASSANDRA_KEYSPACE', 'cassandra_final_project')
KEYSPACE_REPLICATION = os.getenv('CASSANDRA_REPLICATION_FACTOR', 1)
CREATE_KEYSPACE = f"""
    CREATE KEYSPACE IF NOT EXISTS {KEYSPACE_NAME}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': {KEYSPACE_REPLICATION} }}
"""
DELETE_KEYSPACE = F"""
    DROP KEYSPACE IF EXISTS {KEYSPACE_NAME}
"""
#####
CREATE_TABLE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT,
        email TEXT,
        name TEXT,
        phone_number TEXT,
        PRIMARY KEY (email)
    )
"""
INSERT_USER = """
    INSERT INTO users(id, email, name, phone_number)
    VALUES(?, ?, ?, ?)
"""
DELETE_ALL_USERS = """
    TRUNCATE users
"""
SELECT_USER = """
    SELECT id, name, phone_number
    FROM users
    WHERE email = ?
"""
#####
CREATE_TABLE_COURSES_BY_DATE = """
    CREATE TABLE IF NOT EXISTS courses_by_date (
        user_id TEXT,
        course_id TEXT,
        course_name TEXT,
        start_date DATE,
        end_date DATE,
        final_grade FLOAT,
        PRIMARY KEY (user_id, end_date)
    ) WITH CLUSTERING ORDER BY (end_date DESC)
"""
CREATE_TABLE_COURSES_BY_GRADE = """
    CREATE TABLE IF NOT EXISTS courses_by_grade (
        user_id TEXT,
        course_id TEXT,
        course_name TEXT,
        start_date DATE,
        end_date DATE,
        final_grade FLOAT,
        PRIMARY KEY (user_id, final_grade)
    ) WITH CLUSTERING ORDER BY (final_grade DESC)
"""
INSERT_COURSE = lambda table: f"""
    INSERT INTO {table} (user_id, course_id, course_name, start_date, end_date, final_grade)
    VALUES(?, ?, ?, ?, ?, ?);
"""
DELETE_ALL_COURSES = lambda table: f"""
    TRUNCATE {table}
"""
SELECT_COURSES_ALL = """
    SELECT course_id, course_name, start_date, end_date, final_grade
    FROM courses_by_date
    WHERE user_id = ?
"""
SELECT_COURSES_BY_DATE_RANGE = """
    SELECT course_id, course_name, start_date, end_date, final_grade
    FROM courses_by_date
    WHERE user_id = ? AND end_date <= ?
"""
SELECT_COURSES_ACTIVE = """
    SELECT course_id, course_name, start_date, end_date, final_grade
    FROM courses_by_date
    WHERE user_id = ? AND end_date >= ?
"""
SELECT_COURSES_BY_GRADE = """
    SELECT course_id, course_name, start_date, end_date, final_grade
    FROM courses_by_grade
    WHERE user_id = ? AND final_grade >= ? AND final_grade <= ?
"""

def loadSchema():
    connection = DBconnections.CASSANDRA
    connection.execute(CREATE_KEYSPACE)
    connection.set_keyspace(KEYSPACE_NAME)
    connection.execute(CREATE_TABLE_USERS)
    connection.execute(CREATE_TABLE_COURSES_BY_DATE)
    connection.execute(CREATE_TABLE_COURSES_BY_GRADE)

# def deleteSchema():
#     connection = DBconnections.CASSANDRA
#     connection.execute(DELETE_KEYSPACE)

def loadData():
    deleteData()
    connection = DBconnections.CASSANDRA
    data = DBconnections.DATA
    courses = {doc["id"]: doc for doc in data["courses"]}
    insertUserPrepared = connection.prepare(INSERT_USER)
    insertCourseDatePrepared = connection.prepare(INSERT_COURSE("courses_by_date"))
    insertCourseGradePrepared = connection.prepare(INSERT_COURSE("courses_by_grade"))
    for doc in data["users"]:
        connection.execute(insertUserPrepared, [doc["id"], doc["email"], doc["name"], doc["phone_number"]])
        for enrollment in doc["suscribed"]:
            course = courses[enrollment["course_id"]]
            arguments = [doc["id"], course["id"], course["name"], course["start_date"], course["end_date"], enrollment["final_grade"]]
            connection.execute(insertCourseDatePrepared, arguments)
            connection.execute(insertCourseGradePrepared, arguments)

def deleteData():
    connection = DBconnections.CASSANDRA
    connection.execute(DELETE_ALL_USERS)
    connection.execute(DELETE_ALL_COURSES("courses_by_date"))
    connection.execute(DELETE_ALL_COURSES("courses_by_grade"))

def getUserData():
    email = input("Email: ")
    connection = DBconnections.CASSANDRA
    prepared = connection.prepare(SELECT_USER)
    data = connection.execute(prepared, [email])
    if data:
        print(f"Name: {data[0].name}\nPhone number: {data[0].phone_number}")
        return data[0].id
    print("User not found")
    return None

def getAllCourses():
    user_id = getUserData()
    if not user_id:
        return
    connection = DBconnections.CASSANDRA
    prepared = connection.prepare(SELECT_COURSES_ALL)
    data = connection.execute(prepared, [user_id])
    pagination(data)

def getCoursesByDateRange():
    user_id = getUserData()
    if not user_id:
        return
    start_date = input("From (yyyy-mm-dd): ")
    end_date = input("Until (yyyy-mm-dd): ")
    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except:
        print("Invalid dates")
        return
    connection = DBconnections.CASSANDRA
    prepared = connection.prepare(SELECT_COURSES_BY_DATE_RANGE)
    data = connection.execute(prepared, [user_id, end_date])
    data = [row for row in data if start_date <= datetime.datetime.strptime(str(row.start_date), "%Y-%m-%d")]
    pagination(data)

def getActiveCourses():
    user_id = getUserData()
    if not user_id:
        return
    end_date = datetime.datetime.now()
    connection = DBconnections.CASSANDRA
    prepared = connection.prepare(SELECT_COURSES_ACTIVE)
    data = connection.execute(prepared, [user_id, end_date])
    pagination(data)

def getCoursesByFinalGrade():
    user_id = getUserData()
    if not user_id:
        return
    lowLimit = input("Minimum grade (0.0-100.0): ")
    lowLimit = float(lowLimit) if lowLimit.isdecimal() else 0
    highLimit = input("Maximum grade (0.0-100.0): ")
    highLimit = float(highLimit) if highLimit.isdecimal() else 100
    connection = DBconnections.CASSANDRA
    prepared = connection.prepare(SELECT_COURSES_BY_GRADE)
    data = connection.execute(prepared, [user_id, lowLimit, highLimit])
    pagination(data)

def pagination(data):
    showRows = True
    for row in data:
        print("\n".join(
            [f"\t{key}: {value}" for key, value in [("course_id", row.course_id),
                                                    ("course_name", row.course_name),
                                                    ("start_date", row.start_date),
                                                    ("end_date", row.end_date),
                                                    ("final_grade", round(row.final_grade, 2))]]
        ))
        showRows = input("Type ENTER to show more rows, other character to scape: ") == ""
        if not showRows:
            break