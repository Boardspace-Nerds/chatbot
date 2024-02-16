import openai
import os
from dotenv import load_dotenv
from llama_index.core import SQLDatabase
from llama_index.core.indices.struct_store import (
    NLSQLTableQueryEngine,
    SQLTableRetrieverQueryEngine,
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import VectorStoreIndex
from sqlalchemy import create_engine, MetaData, Table, Column, String, Numeric, ForeignKey, insert, text
from flask import Flask, request

app = Flask(__name__)

#configure openAI key
load_dotenv()
openai.api_key=os.getenv('openai_key')

# Create SQLALchemy engine and metadata
engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5433/postgres')
metadata_obj = MetaData()

#create database schema
departments = Table(
    'departments',
    metadata_obj,
    Column('department', String(30), primary_key=True),
    Column('funding', Numeric),
    Column('ranking', Numeric)
)
courses = Table(
    'courses',
    metadata_obj,
    Column('code', String(8), primary_key=True),
    Column('name', String(80), nullable=False, unique=True),
    Column('department', String(30), ForeignKey('departments', ondelete="CASCADE"), nullable=False)
)
professors = Table(
    'professors',
    metadata_obj,
    Column('name', String(30), primary_key=True),
    Column('age', Numeric),
    Column('salary', Numeric),
    Column('department', String(30), ForeignKey('departments', ondelete="CASCADE"), nullable=False),
)
offerings = Table(
    'offerings',
    metadata_obj,
    Column('code', String(8), ForeignKey('courses', ondelete="CASCADE"), nullable=False),
    Column('sectionnum', Numeric, nullable=False),
    Column('name', String(30), ForeignKey('professors', ondelete="CASCADE"), nullable=False)
)

metadata_obj.drop_all(engine)


#create new tables
metadata_obj.create_all(engine)

#insert rows into database
department_rows = [
    {'department': 'Computer Science', 'funding':10000, 'ranking':1},
    {'department': 'English', 'funding':100, 'ranking':3},
    {'department': 'Math', 'funding':10000, 'ranking':2}
]
for row in department_rows:
    stmt = insert(departments).values(**row)
    with engine.connect() as connection:
        cursor = connection.execute(stmt)
        connection.commit()

course_rows = [
    {'code': 'CPSC 101', 'name': 'Introduction to Computer Science', 'department':'Computer Science'},
    {'code': 'CPSC 212', 'name': 'Data Structures and Algorithms', 'department':'Computer Science'},
    {'code': 'CPSC 222', 'name': 'Machine learning', 'department':'Computer Science'},
    {'code': 'MATH 101', 'name': 'Calculus', 'department':'Math'},
    {'code': 'MATH 201', 'name': 'Linear Alegbra', 'department':'Math'},
    {'code': 'ENGL 150', 'name': 'Essay Writing', 'department':'English'},
]
for row in course_rows:
    stmt = insert(courses).values(**row)
    with engine.connect() as connection:
        cursor = connection.execute(stmt)
        connection.commit()

professor_rows = [
    {'name': 'Bill', 'age':52, 'salary':10000, 'department': 'Computer Science'},
    {'name': 'Bob', 'age':36, 'salary':8000, 'department': 'Computer Science'},
    {'name': 'Joe', 'age':31, 'salary':5000, 'department': 'Math'},
    {'name': 'Eris', 'age':29, 'salary':6000, 'department': 'English'},
]
for row in professor_rows:
    stmt = insert(professors).values(**row)
    with engine.connect() as connection:
        cursor = connection.execute(stmt)
        connection.commit()

offering_rows = [
    {'code': 'CPSC 101', 'sectionnum': 101, 'name': 'Bob'},
    {'code': 'CPSC 101', 'sectionnum': 102, 'name': 'Joe'},
    {'code': 'CPSC 212', 'sectionnum': 101, 'name': 'Bob'},
    {'code': 'CPSC 212', 'sectionnum': 200, 'name': 'Bill'},
    {'code': 'CPSC 222', 'sectionnum': 1000, 'name': 'Bill'},
    {'code': 'MATH 101', 'sectionnum': 000, 'name': 'Joe'},
    {'code': 'MATH 201', 'sectionnum': 000, 'name': 'Joe'},
    {'code': 'ENGL 150', 'sectionnum': 111, 'name': 'Eris'},
]

for row in offering_rows:
    stmt = insert(offerings).values(**row)
    with engine.connect() as connection:
        cursor = connection.execute(stmt)
        connection.commit()

# Connect llamindex to the PostgreSQL engine, naming the table we will use
sql_database = SQLDatabase(engine, include_tables=['courses', 'departments', 'professors', 'offerings'])
query_engine = NLSQLTableQueryEngine(sql_database)
# #stores the table schema for specified tables
# node_mapping = SQLTableNodeMapping(sql_database)
# table_schema_objs = [
#     (SQLTableSchema(table_name='courses')),
#     (SQLTableSchema(table_name='departments')),
#     (SQLTableSchema(table_name='professors')),
#     (SQLTableSchema(table_name='offerings')),
# ]

# obj_index = ObjectIndex.from_objects(
#     table_schema_objs,
#     node_mapping,
#     VectorStoreIndex,
# )

# #creates a query engine based on our nodes above
# query_engine = SQLTableRetrieverQueryEngine(
#     sql_database, obj_index.as_retriever(similarity_top_k=1)
# )

#sample query route
@app.route('/query')
def query():
    queryString = request.args.get('str')
    response = query_engine.query(queryString)
    print(response.metadata['sql_query'])
    print(response.metadata)
    return str(response)

#debugging route
@app.route('/test')
def testSQL():
    with engine.connect() as connection:
        query = connection.exec_driver_sql("SELECT name FROM courses WHERE department = 'Computer Science'")
        return(str(query.fetchall()))


if __name__ == '__main__':
    app.run()