CREATE (e1:Employee {name: "Jan", surname: "Maricn", position: "Developer"})
CREATE (e2:Employee {name: "Anna", surname: "Smith", position: "Designer"})
CREATE (e3:Employee {name: "Bob", surname: "Johnson", position: "Manager"})
CREATE (e4:Employee {name: "Emily", surname: "Brown", position: "Analyst"})
CREATE (e5:Employee {name: "David", surname: "Jones", position: "Developer"})
CREATE (e6:Employee {name: "Sophia", surname: "Miller", position: "Designer"})
CREATE (e7:Employee {name: "Michael", surname: "Davis", position: "Manager"})
CREATE (e8:Employee {name: "Olivia", surname: "Wilson", position: "Analyst"})
CREATE (e9:Employee {name: "William", surname: "Moore", position: "Developer"})
CREATE (e10:Employee {name: "Emma", surname: "Johnson", position: "Designer"})
CREATE (e11:Employee {name: "Daniel", surname: "White", position: "Manager"})
CREATE (e12:Employee {name: "Ava", surname: "Taylor", position: "Analyst"})


CREATE (d1:Department {name: "IT"})
CREATE (d2:Department {name: "Design"})
CREATE (d4:Department {name: "Analysis"})


CREATE
    (e1)-[:WORKS_IN]->(d1),
    (e5)-[:WORKS_IN]->(d1),
    (e9)-[:WORKS_IN]->(d1)


CREATE
    (e2)-[:WORKS_IN]->(d2),
    (e6)-[:WORKS_IN]->(d2),
    (e10)-[:WORKS_IN]->(d2)


CREATE
    (e3)-[:WORKS_IN]->(d1),
    (e7)-[:WORKS_IN]->(d2),
    (e11)-[:WORKS_IN]->(d4)


CREATE
    (e4)-[:WORKS_IN]->(d4),
    (e8)-[:WORKS_IN]->(d4),
    (e12)-[:WORKS_IN]->(d4)



CREATE
    (e3)-[:MANAGES]->(e1),
    (e3)-[:MANAGES]->(e2),
    (e3)-[:MANAGES]->(e4),
    (e3)-[:MANAGES]->(d1)

CREATE
    (e7)-[:MANAGES]->(e5),
    (e7)-[:MANAGES]->(e6),
    (e7)-[:MANAGES]->(e8),
    (e7)-[:MANAGES]->(d2)

CREATE
    (e11)-[:MANAGES]->(e9),
    (e11)-[:MANAGES]->(e10),
    (e11)-[:MANAGES]->(e12),
    (e11)-[:MANAGES]->(d4)
