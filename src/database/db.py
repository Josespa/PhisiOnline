"""
Config Database postgresql
"""
SERVER = 'localhost'
DATABASE = 'phisionline'
UID = 'flask_db'
PWD = 'flask_db'

connection_string = "postgresql://"+UID+":"+PWD+"@"+SERVER+"/"+DATABASE
