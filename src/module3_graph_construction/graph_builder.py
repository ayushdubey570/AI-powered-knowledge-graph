import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_PASSWORD:
    raise ValueError("❌ Error: Missing Neo4j credentials in .env file.")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(CURRENT_DIR, '../../data/processed/extracted_triples.json')

class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_graph_from_json(self, json_file_path):
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Could not find {json_file_path}")
            return

        print(f"🔄 Connecting to Neo4j... Processing {len(data)} records.")
        
        with self.driver.session() as session:
            for item in data:
                try:
                    session.execute_write(self._create_nodes_and_relationships, item)
                    print(f"✅ Processed Ticket #{item.get('ticket_id')}")
                except Exception as e:
                    print(f"❌ Error on Ticket #{item.get('ticket_id')}: {e}")

    @staticmethod
    def _create_nodes_and_relationships(tx, item):
        # 1. --- THE MAGIC FIX: Create Rich Context String ---
        # We combine ALL info into one text block so the AI sees it all at once.
        rich_context = (
            f"Ticket ID: {item['ticket_id']}. "
            f"Customer Demographics: {item['customer_age']} year old {item['customer_gender']}. "
            f"Product: {item['product_purchased']}. "
            f"Issue Description: {item['ticket_description']}. "
            f"Root Cause: {item.get('root_cause', 'Unknown')}."
        )

        # A. Create CUSTOMER
        tx.run("""
            MERGE (c:Customer {email: $email})
            SET c.name = $name, c.age = $age, c.gender = $gender
        """, email=item['customer_email'], name=item['customer_name'], 
             age=item['customer_age'], gender=item['customer_gender'])

        # B. Create PRODUCT
        tx.run("MERGE (p:Product {name: $product_name})", 
               product_name=item['product_purchased'])

        # C. Create TICKET (With the new 'rag_content' field)
        tx.run("""
            MERGE (t:Ticket {id: $ticket_id})
            SET t.status = $status,
                t.description = $desc,
                t.rag_content = $rich_context,  // <--- KEY CHANGE
                t.sentiment = $sentiment,
                t.root_cause = $root_cause,
                t.priority = $priority
        """, ticket_id=item['ticket_id'], status=item['ticket_status'], 
             desc=item['ticket_description'], rich_context=rich_context,
             sentiment=item.get('sentiment'), root_cause=item.get('root_cause'), 
             priority=item['ticket_priority'])

        # D. Relationships
        tx.run("""
            MATCH (c:Customer {email: $email})
            MATCH (t:Ticket {id: $ticket_id})
            MERGE (c)-[:RAISED]->(t)
        """, email=item['customer_email'], ticket_id=item['ticket_id'])

        tx.run("""
            MATCH (t:Ticket {id: $ticket_id})
            MATCH (p:Product {name: $product_name})
            MERGE (t)-[:ABOUT]->(p)
        """, ticket_id=item['ticket_id'], product_name=item['product_purchased'])

if __name__ == "__main__":
    graph_builder = KnowledgeGraphBuilder(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        graph_builder.create_graph_from_json(INPUT_FILE)
        print("\n🎉 Graph Built Successfully!")
    finally:
        graph_builder.close()