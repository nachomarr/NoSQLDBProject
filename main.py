from dotenv import load_dotenv
from src.databases import DBconnections
import src.cassandra as cassandra

import src.menu as menu

load_dotenv()
DBconnections.startConnections()
cassandra.loadSchema()

menu.runApp()
DBconnections.closeConnections()