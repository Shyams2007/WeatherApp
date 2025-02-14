import MySQLdb.cursors
import re

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="Shyam13HA",
    password="Shyam1234@",
    database = "mydatabase"
  ) 

def getdb():  
  return mydb

mycursor = getdb().cursor()
sql =""

def create_table():
    
  c = mycursor

  sql ='''CREATE TABLE IF NOT EXISTS searches (
    id INT NOT NULL AUTO_INCREMENT, 
    city VARCHAR(256) NOT NULL, 
    temperature VARCHAR(50),
    description VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    emailId VARCHAR(255),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS user (
    id VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    profile_pic TEXT NOT NULL,
    PRIMARY KEY (id)
);'''
                
  c.execute(sql)      
  #mydb.commit()
  getdb().close()

# Initialise the database
if __name__ == "__main__":
    create_table()
