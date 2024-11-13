import random
import string
import json
from datetime import datetime, timedelta
import uuid

# Helper functions
def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_phone():
    return ''.join(random.choices(string.digits, k=10))

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# Data generation functions
def generate_user():
    return {
        "_id": str(uuid.uuid4()),
        "name": random.choice(["Luis","Raúl","Juan","David"]),
        "email": f"{random_string(5)}@example.com",
        "phoneNumber": random_phone()
    }

def generate_course():
    start_date = datetime.now()
    end_date = start_date + timedelta(days=random.randint(30, 120))  # Course length between 1-4 months
    return {
        "_id": str(uuid.uuid4()),
        "name": f"Curso {random_string(5)}",
        "description": "El Mejor curso.",
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "instructorId": str(uuid.uuid4()),
        "registrationSpaces": random.randint(10, 100),
        "topics": [random_string(5) for _ in range(random.randint(2, 5))],
        "mode": random.choice(["online", "offline", "hibrido"]),
        "schedule": f"{random.randint(1, 5)} Sesiones por semana",
        "sessionsLink": f"https://example.com/course/{random_string(8)}"
    }

def generate_enrolled_course(user_ids, course_ids):
    return {
        "userId": random.choice(user_ids),
        "courseId": random.choice(course_ids),
        "finalGrade": random.uniform(50, 100)  # Grades between 50-100
    }

# Generate datasets
def generate_dataset(num_users=10, num_courses=5, num_enrollments=20):
    users = [generate_user() for _ in range(num_users)]
    courses = [generate_course() for _ in range(num_courses)]
    user_ids = [user["_id"] for user in users]
    course_ids = [course["_id"] for course in courses]
    enrollments = [generate_enrolled_course(user_ids, course_ids) for _ in range(num_enrollments)]

    return {
        "users": users,
        "courses": courses,
        "enrolledCourses": enrollments
    }

# Save dataset to JSON file
def save_to_json(data, filename="dataset.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Dataset saved to {filename}")

# Main function to generate and save dataset
if __name__ == "__main__":
    dataset = generate_dataset(num_users=4, num_courses=5, num_enrollments=20)
    save_to_json(dataset)
