from cassandra.cluster import Cluster
from pymongo import MongoClient
import pydgraph
import os
import json

class DBconnections:
    DATA = None
    CASSANDRA = None
    MONGO = None
    DGRAPH = None
    __url = None
    __cluster = None
    __mongoClient = None
    __dgraphClientStub = None

    def startConnections():
        with open("data/dataset.json", "r") as file:
            DBconnections.DATA = json.loads(file.read())
        DBconnections.__url = os.getenv('DB_URL')
        DBconnections.__startCassandraConnection()
        DBconnections.__startMongoConnection()
        DBconnections.__startDgraphConnection()

    def closeConnections():
        DBconnections.__closeCassandraConnection()
        DBconnections.__closeMongoConnection()
        DBconnections.__closeDgraphConnection()

    def __startCassandraConnection():
        cassandraUrl = os.getenv('CASSANDRA_URL', DBconnections.__url)
        DBconnections.__cluster = Cluster(cassandraUrl.split(','))
        DBconnections.CASSANDRA = DBconnections.__cluster.connect()

    def __closeCassandraConnection():
        DBconnections.CASSANDRA.shutdown()
        DBconnections.__cluster.shutdown()

    def __startMongoConnection():
        mongoUrl = os.getenv('MONGODB_URL', f'mongodb://{DBconnections.__url}:27017')
        dbName = os.getenv('MONGODB_DBNAME', 'MongoDBFinalProject')
        DBconnections.__mongoClient = MongoClient(mongoUrl)
        DBconnections.MONGO = DBconnections.__mongoClient[dbName]

    def __closeMongoConnection():
        DBconnections.__mongoClient.close()

    def __startDgraphConnection():
        dgraphUrl = os.getenv('DGRAPH_URL', f'{DBconnections.__url}:9080')
        DBconnections.__dgraphClientStub = pydgraph.DgraphClientStub(dgraphUrl)
        DBconnections.DGRAPH = pydgraph.DgraphClient(DBconnections.__dgraphClientStub)

    def __closeDgraphConnection():
        DBconnections.__dgraphClientStub.close()