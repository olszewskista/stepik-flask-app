# Employee Managemet Flask Api

Live version: 

## Endpoins:
#### 1. GET - "/employees"
- Get all employees
- Available options: filterKey, filterVal, sortKey, sortOrder
- Example: 
```/employees?filterKey=department&filterVal=IT&sortKey=name&sortOrder=ASC```

#### 2. POST - "/employees"
- Add new employee
- Example request body:
```json
 {
	"name": "Rat",
    "surname": "Dar",
    "position": "Developer",
    "department": "IT"
}
```

#### 3. PUT - "/employees/:id"
- Update existing employee
- Request body same as above

#### 4. DELETE - "/employees/:id"
- Delete existing employee
- Example: ```/employees/12```

#### 5. GET - "/employees/:id/subordinates"
- Get subordiates of a manager
- Example: ```/employees/2```

#### 6. GET - "/departments/:name"
- Get info about a department
- Example: ```/departments/Design```

#### 7. GET - "/departments"
- Get all departments
- Example: ```/departments```

#### 8. GET - "/departments/:name/employees"
- Get employees working in desired department
- Example: ```/departments/Design/employees```

