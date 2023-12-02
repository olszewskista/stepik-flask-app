from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from neo4j import GraphDatabase

load_dotenv()

app = Flask(__name__)

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))
driver.verify_authentication()
driver.verify_connectivity()

#funkcja pomocnicza do zwaracania pracownikow
def get_employees(tx, filterKey, filterVal, sortKey, sortOrder):
    query = "MATCH (e:Employee)-[r:WORKS_IN]->(d:Department) "
    if filterKey and filterVal:
        query += f"WHERE e.{filterKey} = '{filterVal}' "
    query += "RETURN ID(e) as id, e.name as name, e.surname as surname, e.position as position, d.name as department "
    if sortKey and sortOrder:
        query += f"ORDER BY e.{sortKey} {sortOrder}"
    result = tx.run(query).data()
    return result

#zwracanie pracownikow z mozliwoscia filtrowania i sortowania - endpoint
@app.route("/employees", methods=["GET"])
def get_employees_route():
    filterKey = request.args.get('filterKey', default=None, type=str)
    filterVal = request.args.get('filterVal', default=None, type=str)
    sortKey = request.args.get('sortKey', default=None, type=str)
    sortOrder = request.args.get('sortOrder', default="ASC", type=str)

    with driver.session() as session:
        result = session.execute_read(get_employees, filterKey, filterVal, sortKey, sortOrder)
    return jsonify(result), 200

#dodanie pracownika
def add_employee(tx, name, surname, position, department):
    query = (
        "MATCH (d:Department {name: $department})"
        "CREATE (e:Employee {name: $name, surname: $surname, position: $position}),"
        "(e)-[r:WORKS_IN]->(d)"
        )
    print("dddd")
    tx.run(query, name=name, surname=surname, position=position, department=department)

#dodanie managera
def add_manager(tx, name, surname, position, department):
    query = (
        "MATCH (d:Department {name: $department})"
        "CREATE (e:Employee {name: $name, surname: $surname, position: $position}),"
        "(e)-[r:WORKS_IN]->(d),"
        "(e)-[r2:MANAGES]->(d)"
        )
    tx.run(query, name=name, surname=surname, position=position, department=department)


#dodanie nowego pracownika/managera - endpoint
@app.route("/employees", methods=["POST"])
def add_employee_route():
    name = request.json.get("name")
    surname = request.json.get("surname")
    position = request.json.get("position")
    department = request.json.get("department")

    if any(not x for x in [name, surname, position, department]):
        return jsonify({"message": "Please enter correct data"}), 400
    checkQuery = f"MATCH (n:Employee {{name: '{name}', surname: '{surname}'}}) RETURN n"

    with driver.session() as session:
        checkForUniqe = session.run(checkQuery).single()
        if checkForUniqe:
            return jsonify({"message": "Please enter uniqe name and surname"})
        if position == "Manager":
            session.execute_write(add_manager, name, surname, position, department)
        else:
            session.execute_write(add_employee, name, surname, position, department)
    return jsonify({"message": "Employee has been added"})

#funcka pomocnicza do aktualizacji danych
def update_employee(tx, id, data):
    query = f"MATCH (e:Employee)-[r]->(d) WHERE ID(e) = {id} "
    name = data.get("name")
    surname = data.get("surname")
    position = data.get("position")
    department = data.get("department")

    if department:
        query += f"MATCH (d2:Department {{name: '{department}'}}) "

    if name:
        query += f"SET e.name = '{name}' "

    if surname:
        query += f"SET e.surname = '{surname}' "
        
    if position and position == "Manager":
        query += (
            f"SET e.position = '{position}' "
            f"MERGE (e)-[:MANAGES]->(d2) "
            )
    elif position:
        query += f"SET e.position = '{position}' "

    if department:
        query += (
            "DELETE r "
            f"MERGE (e)-[:WORKS_IN]->(d2) "
            )

    query += "RETURN e"
    result = tx.run(query , id=id).data()
    return result

#aktualizacja danych endpoint
@app.route("/employees/<id>", methods=["PUT"])
def update_employee_route(id):
    data = request.get_json()
    with driver.session() as session:
        employeeWithId = session.run(f"MATCH (e:Employee) WHERE ID(e) = {id} RETURN e").single()
        if not employeeWithId:
            return jsonify({"message": "Employee with this id doesnt exist"})
        
        updatedEmployee = session.execute_write(update_employee, id, data)

    return jsonify({"message": "Employee has been updated", "employee": updatedEmployee[0]["e"]}), 200

#funkcja pomocnicza do usuwania, gdy usuwamy managera usuwamy caly departament
def delete_employee(tx, id):
    checkIsManager = f"MATCH (e:Employee) WHERE ID(e) = {id} RETURN e.position as position"
    position = tx.run(checkIsManager).data()[0]["position"]
    if position == "Manager":
        query = f"MATCH (e:Employee)-[:MANAGES]->(d:Department) WHERE ID(e) = {id} DETACH DELETE e, d"
        tx.run(query)
        return "Manager and Department"
    else:
        query = f"MATCH (e:Employee) WHERE ID(e) = {id} DETACH DELETE e"
        tx.run(query)
        return "Employee"
        

#usuwanie pracownika - endpoint
@app.route("/employees/<id>", methods=["DELETE"])
def delete_employee_route(id):
    with driver.session() as session:
        employeeWithId = session.run(f"MATCH (e:Employee) WHERE ID(e) = {id} RETURN e").single()
        if not employeeWithId:
            return jsonify({"message": "Employee with this id doesnt exist"})
        result = session.execute_write(delete_employee, id)
    return jsonify({"message": f"{result} has been deleted"})

#funkcja pomocnicza dla podwladnych
def get_subordinates(tx, id):
    query = f"MATCH (e1:Employee)-[r:MANAGES]->(e2:Employee) WHERE ID(e1) = {id} RETURN e2"
    result = tx.run(query).data()
    final = [res["e2"] for res in result]
    return final

#zwracanie podwladnych - endpoint
@app.route("/employees/<id>/subordinates", methods=["GET"])
def get_subordinates_route(id):
    with driver.session() as session:
        employeeWithId = session.run(f"MATCH (e:Employee) WHERE ID(e) = {id} RETURN e").single()
        if not employeeWithId:
            return jsonify({"message": "Employee with this id doesnt exist"}), 404
        sub = session.execute_read(get_subordinates, id)
    return jsonify({"subordinates": sub}), 200

#funkcja pomocnicza zwracajaca informacje o zadanym departamencie
def get_department_info(tx, name):
    query = f"MATCH (e:Employee)-[r:WORKS_IN]->(d:Department) WHERE d.name = '{name}' RETURN count(e) as number"
    numberOfEmployees = tx.run(query).data()[0]["number"]
    query2 = f"MATCH (e:Employee)-[r:WORKS_IN]->(d:Department) WHERE d.name = '{name}' AND e.position = 'Manager' RETURN e"
    manager = tx.run(query2).data()[0]["e"]
    return (numberOfEmployees, manager)

#zwrot informacji o departamencie - endpoint
@app.route("/departments/<name>", methods=["GET"])
def get_department_info_route(name):
    with driver.session() as session:
        department = session.run(f"MATCH (d:Department) WHERE d.name = '{name}' RETURN d").single()
        if not department:
            return jsonify({"message": "This department doesnt exist"}), 404
        result = session.execute_read(get_department_info, name)
    return jsonify({"number of employees": result[0], "manager": result[1]})

#funkcja pomocnicza zwracajaca wszystkie departamenty z mozliwoscia sortowania
def get_departments(tx, filterKey, filterVal, sortKey, sortOrder):
    query = "MATCH (d:Department) "
    if filterKey and filterVal:
        query += f"WHERE e.{filterKey} = '{filterVal}' "
    query += "RETURN d.name as departmentName "
    if sortKey and sortOrder:
        query += f"ORDER BY e.{sortKey} {sortOrder}"
    result = tx.run(query).data()
    return result

#zwracanie pracownikow z mozliwoscia filtrowania i sortowania - endpoint
@app.route("/departments", methods=["GET"])
def get_departments_route():
    filterKey = request.args.get('filterKey', default=None, type=str)
    filterVal = request.args.get('filterVal', default=None, type=str)
    sortKey = request.args.get('sortKey', default=None, type=str)
    sortOrder = request.args.get('sortOrder', default="ASC", type=str)

    with driver.session() as session:
        result = session.execute_read(get_departments, filterKey, filterVal, sortKey, sortOrder)
    return jsonify(result), 200

#funkca pomocnicza zwracajaca wszystkich pracownikow
def get_departments_employees(tx, name):
    query = f"MATCH (e:Employee)-[r:WORKS_IN]->(d:Department) WHERE d.name = '{name}' RETURN e"
    employees = tx.run(query).data()
    final = [employee["e"] for employee in employees]
    return final

#zwracanie wszystkich pracownikow - endpoint
@app.route("/departments/<name>/employees", methods=["GET"])
def get_departments_employees_route(name):
    with driver.session() as session:
        department = session.run(f"MATCH (d:Department) WHERE d.name = '{name}' RETURN d").single()
        if not department:
            return jsonify({"message": "This department doesnt exist"}), 404
        result = session.execute_read(get_departments_employees, name)
    return jsonify({"employees": result})
        