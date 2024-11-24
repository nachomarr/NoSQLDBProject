from dotenv import load_dotenv
from src.databases import DBconnections
import src.cassandra as cassandra
import src.dgraph as dgraph
import src.menu as menu

load_dotenv()
DBconnections.startConnections()
cassandra.loadSchema()
dgraph.loadSchema(DBconnections.DGRAPH)
menu.runApp()
DBconnections.closeConnections()