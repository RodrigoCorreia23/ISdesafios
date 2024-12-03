from flask import Flask
import mysql.connector


app = Flask(__name__)   

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/db')
def db_connect():
    connection = mysql.connector.connect(
        host = 'db',
        user = 'root',
        password = 'root+password',
        database = 'mydb'
    )
    cursor = connection.cursor()
    cursor.execute("SELECT 'Conexao com o banco de dados realizada com sucesso!'")
    result = cursor.fetchone()
    return result [0]

if __name__ == '__main__':
    app.run(host='0.0.0.0')