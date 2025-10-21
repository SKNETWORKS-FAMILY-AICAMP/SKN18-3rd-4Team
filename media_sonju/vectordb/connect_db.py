import os
from urllib.parse import urlparse
from .Check_Singleton import SingletonDatabase
# from dotenv import load_dotenv

def connect_DB(connect_str="CONNECTION_STRING") -> dict:
    #load_dotenv()
    conn_url = os.getenv(connect_str)
    url = urlparse(conn_url)
    config = { "host": url.hostname, 
                    "port": url.port, 
                    "user": url.username, 
                    "password": url.password, 
                    "dbname": url.path.lstrip('/')
            }
    return SingletonDatabase(config)