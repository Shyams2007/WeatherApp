import MySQLdb.cursors
import re

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="Shyam13HA",
  password="Shyam1234@",
  database = "mydatabase"
)
mycursor = mydb.cursor()
sql =""

def create_table():
    
  c = mycursor

  sql ='''CREATE TABLE IF NOT EXISTS searches (
              id int(11) NOT NULL AUTO_INCREMENT, 
               city VARCHAR(50) NOT NULL, 
               temperature VARCHAR(50),
               description VARCHAR(255),
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
               PRIMARY KEY(id))'''
                
  c.execute(sql)      
  mydb.commit()
  mydb.close()

# Initialise the database
if __name__ == "__main__":
    create_table()
