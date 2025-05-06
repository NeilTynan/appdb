from neo4j import GraphDatabase

def connect_neo4j():
    global driver
    url = "neo4j://localhost:7687"
    driver = GraphDatabase.driver(url, auth=("neo4j", "neo4jneo4j"), max_connection_lifetime=1000)

def test_neo4j_connection():
    if not 'driver' in globals():
        connect_neo4j()  # Ensure that Neo4j driver is connected
    
    with driver.session() as session:
        result = session.run("RETURN 'Hello, Neo4j!' AS message")
        for record in result:
            print(record["message"])

# Call the test function
test_neo4j_connection()