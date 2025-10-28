import mysql as db
import mysql.connector
import json

def connect():
    with open('data/conection.json', 'r') as file:
        config = json.load(file)
    
    connection = mysql.connector.connect(
        host=config['host'],
        user=config['username'],
        password=config['password'],
        database=config['database'],
        collation='utf8mb4_unicode_ci'
    )
    return connection

def read_data(query):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def write_data(query, data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, data)
    conn.commit()
    cursor.close()
    conn.close()

def update_data(query, data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, data)
    conn.commit()
    cursor.close()
    conn.close()

def delete_data(query, data):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, data)
    conn.commit()
    cursor.close()
    conn.close()

