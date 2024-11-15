# Para crear contenedores
Cassandra:
    docker run --name cassandradbProyecto -d -p 9042:9042 cassandra

Mongo:
    docker run --name mongodbProyecto -d -p 27017:27017 mongo

Dgraph:
    docker run --name dgraphProyecto -d -p 8080:8080 -p 9080:9080 dgraph/standalone:latest

# Instalar requerimientos
pip install -r requirements.txt

# INICIAR LA CONEXION ENTRE MONGO Y PYTHON
python3 -m uvicorn main:app --reload




