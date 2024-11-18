
# INSTITUTO TECNOLÓGICO Y DE ESTUDIOS SUPERIORES DE OCCIDENTE
# Proyecto final: Aprende++
## Bases de datos no relacionales
## Profesora Anmol Khatri Pathry
## Integrantes del equipo:
## Ignacio Márquez Robles
## Luis Antonio Cuaquentzi Avendaño
## Jesús Alejandro Toral Iñiguez

# Pasos para iniciar la aplicación de forma local

### Crear los contenedores
Cassandra:
    `docker run --name cassandradbProyecto -d -p 9042:9042 cassandra`

Mongo:
    `docker run --name mongodbProyecto -d -p 27017:27017 mongo`

Dgraph:
    `docker run --name dgraphProyecto -d -p 8080:8080 -p 9080:9080 dgraph/standalone:latest`

### Crear un archivo .env
Colocar la variable `DB_URL=localhost` para realizar la conexión a los contenedores de Docker.

### Crear el ambiente virtual de Python
Nota: se utilizó la versión de Python 3.10.8, no todas soportan el driver de cassandra.
`python -m venv ./venv`

### Iniciar el ambiente virtual
En Windows:
`.\venv\Scripts\Activate.ps1`

### Instalar las librerías
`python -m pip install -r requirements.txt`

### Crear el dataset
`python data/generateDataset.py`

### Iniciar la aplicación
`python main.py`

