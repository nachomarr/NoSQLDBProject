import os
import pydgraph
from fastapi import FastAPI
from pymongo import MongoClient
import random
from datetime import datetime
from cassandra.cluster import Cluster



# Conexion a DRAPHDB
DGRAPH_URI = os.getenv('DGRAPH_URI', 'localhost:9080') #Obtenemos el puerto de DGraph

def create_client_stub():
    return pydgraph.DgraphClientStub(DGRAPH_URI)

def create_client(client_stub):
    return pydgraph.DgraphClient(client_stub)

def close_client_stub(client_stub):
    client_stub.close()
    
#Conexion a Mongo

app = FastAPI()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'MongoDBFP')

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(MONGODB_URI)
    app.database = app.mongodb_client[DB_NAME]
    print(f"Connected to MongoDB at: {MONGODB_URI} \n\t Database: {DB_NAME}")
    
@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()
    print("Bye bye...!!")

app = FastAPI()

#Conexion a Cassandra
date_min = datetime(1970, 1, 1, 21, 0)  
date_max = datetime(2099, 12, 30, 21, 0)

CLUSTER_IPS = os.getenv('CASSANDRA_CLUSTER_IPS', 'localhost')
KEYSPACE = os.getenv('CASSANDRA_KEYSPACE', 'investments')
REPLICATION_FACTOR = os.getenv('CASSANDRA_REPLICATION_FACTOR', '1')


def close_cassandra_session(cluster, session):
    if session:
        session.shutdown()
    if cluster:
        cluster.shutdown()
    



def main():
    # Init Client Stub and Dgraph Client
    client_stub = create_client_stub()
    client = create_client(client_stub)
    cluster = Cluster(CLUSTER_IPS.split(','))
    session = cluster.connect()
    print("conectado")
    
if __name__ == "__main__":
    main()