import random
import string
import json
from datetime import datetime, timedelta
import uuid

class DatasetGenerator:
    __NAMES = [
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
    __COURSES = [
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
    __KEYWORDS = [
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
    __NUMBER_ENROLLMENTS = int(len(__COURSES) / 5)
    __NUMBER_FOLLOWS = int(len(__NAMES) / 10)
    __NUMBER_LIKES = int(len(__COURSES) / 5)

    # Generate datasets
    def generate_dataset():
        users = [DatasetGenerator.__generate_user(name) for name in DatasetGenerator.__NAMES]
        courses = [DatasetGenerator.__generate_course(DatasetGenerator.__COURSES[i], DatasetGenerator.__KEYWORDS[i], users) for i in range(len(DatasetGenerator.__COURSES))]
        DatasetGenerator.__generate_enrolled_courses(users, courses)
        DatasetGenerator.__setRelations(users, courses)
        dataset = {
            "users": users,
            "courses": courses
        }
        DatasetGenerator.__save_to_json(dataset)

    # Data generation functions
    def __generate_user(name):
        return {
            "type": "user",
            "id": str(uuid.uuid4()),
            "name": name,
            "email": f"{name.lower()}@example.com",
            "phone_number": DatasetGenerator.__random_phone(),
            "follows": [],
            "likes": [],
            "dislikes": [],
            "suscribed": [],
            "teaches": []
        }

    def __generate_course(course, keywords, users):
        start_date = datetime.now() - timedelta(days=random.randint(0, 365*5))
        end_date = start_date + timedelta(days=random.randint(30, 365))  # Course length between 1-4 months
        instructor = random.choice(users)
        courseId = str(uuid.uuid4())
        instructor["teaches"].append(courseId)
        return {
            "type": "course",
            "id": courseId,
            "name": course,
            "description": f"En este curso aprenderás sobre {course.lower()}",
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "instructor_id": instructor["id"],
            "registration_spaces": random.randint(len(DatasetGenerator.__NAMES), 2*len(DatasetGenerator.__NAMES)),
            "keywords": keywords,
            "mode": random.choice(["online", "offline", "hibrido"])
        }

    def __generate_enrolled_courses(users, courses):
        for i in range(len(users)):
            selectedCourses = [random.choice(courses) for j in range(DatasetGenerator.__NUMBER_ENROLLMENTS)]
            courseIds = set()
            selectedCourses2 = []
            for course in selectedCourses:
                if course["id"] not in courseIds:
                    selectedCourses2.append(course)
                    courseIds.add(course["id"])
            users[i]["suscribed"] = [{ "course_id": course["id"], "final_grade": round(random.uniform(50, 100), 2) }
                                    for course in selectedCourses2 if course["instructor_id"] != users[i]["id"]]

    def __setRelations(users, courses):
        userIds = [user["id"] for user in users]
        courseIds = [course["id"] for course in courses]
        for i in range(len(users)):
            selfId = users[i]["id"]
            randomIds = set([random.choice(userIds) for j in range(DatasetGenerator.__NUMBER_FOLLOWS)])
            randomIds.discard(selfId)
            users[i]["follows"] = list(randomIds)
            users[i]["likes"] = list(set([random.choice(courseIds) for j in range(DatasetGenerator.__NUMBER_LIKES)]))
            users[i]["dislikes"] = list(set([random.choice(courseIds) for j in range(DatasetGenerator.__NUMBER_LIKES)]))

    def __random_phone():
        return ''.join(random.choices(string.digits, k=10))

    # Save dataset to JSON file
    def __save_to_json(data, filename="data/dataset.json"):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print("Dataset generated successfully")

DatasetGenerator.generate_dataset()