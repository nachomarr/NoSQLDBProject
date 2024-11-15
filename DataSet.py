import random
import string
import json
from datetime import datetime, timedelta
import uuid

NAMES = [
    "Miguel", "Carlos", "Alejandro", "Jose", "Manuel", "Ricardo", "Fernando", "Pablo", 
    "Andres", "Antonio", "Marco", "Julio", "Sebastian", "Mario", "Jorge", "Rafael", 
    "Hector", "Adrian", "Enrique", "Santiago", "Armando", "Cristian", "Daniel", 
    "Leonardo", "Tomas", "Ruben", "Ivan", "Emiliano", "Oscar", "Alberto", "Martin", 
    "Esteban", "Mauricio", "Salvador", "Valentin", "Luis", "Raul", "Juan", "David",
    "Maria", "Ana", "Isabel", "Carmen", "Laura", "Sofia", "Daniela", "Lucia", "Valentina",
    "Gabriela", "Mariana", "Alejandra", "Rosa", "Claudia", "Patricia", "Andrea", "Sara", 
    "Paola", "Natalia", "Fernanda", "Victoria", "Julia", "Monica", "Silvia", "Carolina", 
    "Teresa", "Angela", "Josefina", "Alicia", "Beatriz", "Elena", "Cecilia", "Veronica", 
    "Lourdes", "Guadalupe", "Esther"
]
COURSES = [
    "Introducción a la Programación",
    "Desarrollo Web con HTML y CSS",
    "JavaScript para Principiantes",
    "Fundamentos de Python",
    "Programación Orientada a Objetos en Java",
    "Desarrollo de Aplicaciones con React",
    "Desarrollo Backend con Node.js",
    "Bases de Datos SQL y NoSQL",
    "Introducción a Machine Learning",
    "Estructuras de Datos y Algoritmos",
    "Fundamentos de C++",
    "Desarrollo de APIs con Flask",
    "Aplicaciones Móviles con React Native",
    "Programación Funcional en JavaScript",
    "Fundamentos de Redes y Seguridad",
    "Desarrollo con Django",
    "Automatización de Pruebas con Selenium",
    "Análisis de Datos con Python",
    "Inteligencia Artificial Básica",
    "Desarrollo de Videojuegos con Unity",
    "Fundamentos de DevOps",
    "Desarrollo de Microservicios",
    "Desarrollo Full Stack con MERN",
    "Introducción a Blockchain",
    "Desarrollo de Aplicaciones con Vue.js",
    "Programación en Swift para iOS",
    "Machine Learning Avanzado",
    "Procesamiento de Lenguaje Natural",
    "Introducción a Kubernetes",
    "Optimización y Mejores Prácticas en Python"
]
KEYWORDS = [
    ["programación", "introducción", "conceptos básicos"],
    ["desarrollo web", "HTML", "CSS", "frontend"],
    ["JavaScript", "principiantes", "fundamentos", "frontend"],
    ["Python", "fundamentos", "principiantes", "introducción"],
    ["programación orientada a objetos", "Java", "POO", "clases"],
    ["React", "desarrollo web", "frontend", "componentes"],
    ["backend", "Node.js", "servidores", "API"],
    ["bases de datos", "SQL", "NoSQL", "almacenamiento"],
    ["machine learning", "introducción", "IA", "algoritmos"],
    ["estructuras de datos", "algoritmos", "optimización"],
    ["C++", "programación", "fundamentos", "POO"],
    ["API", "Flask", "backend", "desarrollo"],
    ["aplicaciones móviles", "React Native", "frontend", "iOS", "Android"],
    ["programación funcional", "JavaScript", "funciones", "paradigmas"],
    ["redes", "seguridad", "protocolos", "ciberseguridad"],
    ["Django", "backend", "desarrollo web", "Python"],
    ["automatización de pruebas", "Selenium", "testing"],
    ["análisis de datos", "Python", "estadística", "visualización"],
    ["inteligencia artificial", "IA", "algoritmos básicos"],
    ["videojuegos", "Unity", "desarrollo de juegos", "3D"],
    ["DevOps", "implementación continua", "infraestructura"],
    ["microservicios", "arquitectura", "backend", "API"],
    ["full stack", "MERN", "MongoDB", "Express", "React", "Node.js"],
    ["blockchain", "criptomonedas", "contratos inteligentes"],
    ["Vue.js", "frontend", "componentes", "desarrollo web"],
    ["Swift", "iOS", "programación móvil", "Apple"],
    ["machine learning avanzado", "IA", "aprendizaje supervisado"],
    ["procesamiento de lenguaje natural", "NLP", "textos", "IA"],
    ["Kubernetes", "contenedores", "orquestación", "DevOps"],
    ["Python", "optimización", "mejores prácticas", "eficiencia"]
]

# Helper functions
def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_phone():
    return ''.join(random.choices(string.digits, k=10))

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# Data generation functions
def generate_user(name):
    return {
        "_id": str(uuid.uuid4()),
        "name": name,
        "email": f"{name.lower()}@example.com",
        "phoneNumber": random_phone()
    }

def generate_course(course, keywords, users):
    start_date = datetime.now()
    end_date = start_date + timedelta(days=random.randint(30, 120))  # Course length between 1-4 months
    return {
        "_id": str(uuid.uuid4()),
        "name": course,
        "description": f"En este curso aprenderás sobre {course.lower()}",
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "instructorId": random.choice(users)["_id"],
        "registrationSpaces": random.randint(10, 100),
        "keywords": keywords,
        "mode": random.choice(["online", "offline", "hibrido"])
    }

def generate_enrolled_course(user_ids, course_ids):
    course_id, course_instructorId = random.choice(course_ids)
    return {
        "userId": random.choice([_id for _id in user_ids if _id != course_instructorId]),
        "courseId": course_id,
        "finalGrade": round(random.uniform(50, 100), 2)  # Grades between 50-100
    }

# Generate datasets
def generate_dataset(num_enrollments):
    users = [generate_user(name) for name in NAMES]
    courses = [generate_course(COURSES[i], KEYWORDS[i], users) for i in range(len(COURSES))]
    user_ids = [user["_id"] for user in users]
    course_ids = [(course["_id"], course["instructorId"]) for course in courses]
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
    dataset = generate_dataset(20)
    save_to_json(dataset)
