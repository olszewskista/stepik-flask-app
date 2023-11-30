from flask import Flask, request, jsonify
from neo4j import AsyncGraphDatabase
import asyncio
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Konfiguracja połączenia z bazą Neo4j
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

# Klasa zarządzająca połączeniem z bazą Neo4j
class Neo4jDB:
    def __init__(self, uri, username, password):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    async def query(self, query, parameters=None, write=False):
        async with self._driver.session() as session:
            if write:
                await session.write_transaction(self._run, query, parameters)
            else:
                return await session.read_transaction(self._run, query, parameters)

    @staticmethod
    async def _run(tx, query, parameters):
        result = await tx.run(query, **parameters)
        return result.data()

# Inicjalizacja obiektu Neo4jDB
db = Neo4jDB(uri, username, password)

# Endpoint do dodawania pracownika
@app.route('/employee', methods=['POST'])
async def add_employee():
    data = await request.json
    employee_name = data['name']
    department_name = data['department']

    # Dodanie pracownika i przypisanie do departamentu
    query = (
        f"MERGE (e:Employee {{name: '{employee_name}'}})"
        f"MERGE (d:Department {{name: '{department_name}'}})"
        "MERGE (e)-[:WORKS_IN]->(d)"
    )

    await db.query(query, write=True)
    return jsonify({'message': 'Employee added successfully'}), 201

# Endpoint do pobierania listy pracowników w danym departamencie
@app.route('/employees', methods=['GET'])
async def get_employees_in_department():
    query = (
        "MATCH (a:Movie) RETURN a.title as movie"
    )

    result = await db.query(query)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
