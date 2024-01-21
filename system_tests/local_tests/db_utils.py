"""
Database utils for connecting to 
cluster, modifying documents, etc.
"""

import logging
from pymongo import MongoClient, ReturnDocument
from contextlib import contextmanager
import time
import random
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI from the environment variables
URI = os.getenv("URI")

# Redacted for security
DB_NAME = ...
COLLECTION_NAME = ...

def new_student_with_net_id(net_id : str):
    """
    Creates a new student document
    with the given netid and 0 late
    days in their late days dict.

    Parameters:
        net_id (str): NetID of student, like "kgwilson2"
    
    Returns:
        student (dict): student document
    """
    return {
        "net_id": net_id,
        "late_days": {}
    }

@contextmanager
def connect():
    """
    Establish a connection to the MongoDB cluster.

    Returns:
        MongoClient: A MongoDB client instance if the connection is successful.
        None: If the connection fails.
    """
    try:
        # Create a new client and connect to the server
        client = MongoClient(URI, ssl=True, tls=True, tlsAllowInvalidCertificates=True)
        yield client
    except Exception as e:
        logging.error('Failed to connect to MongoDB Cluster. Error: %s', str(e))
        return None
    finally:
        client.close() # Ensure the client is closed even if an exception occurs


def ping():
    """
    Pings the MongoDB cluster.

    Returns:
        str: "pong" if successful
        None: if connection fails
    """
    try:
        with connect() as client:
            client.admin.command('ping')
        return "pong"
    except Exception as e:
        logging.error('Failed to ping MongoDB Cluster. Error: %s', str(e))
        return None


def get_late_days_by_netid(net_id):
    """
    Finds a student document in the
    students collection by netid.

    Parameters:
        net_id (str): NetID of student, like "kgwilson2"

    Returns:
        late_days (list): late days list if found
        None: if student is not found
    """
    try:
        with connect() as client:
            collection = client[DB_NAME][COLLECTION_NAME]
            student = collection.find_one({"net_id" : net_id})
        if student is None:
            return None
        else:
            return student["late_days"]
    except Exception as e:
        logging.error('Failed to get student from MongoDB Cluster. Error: %s', str(e))
        return None

def insert_new_student(net_id, delete_existing : bool):
    """
    Inserts a document for a new
    student into the collection. 

    Parameters:
        net_id (str): NetID of student, like "kgwilson2"
        delete_existing (bool): Should existing documents with the same netid be deleted?
    
    Returns:
        True (bool): if insertion is successful
        False (bool): if insertion fails
    """
    try:
        with connect() as client:
            collection = client[DB_NAME][COLLECTION_NAME]
            if delete_existing:
                collection.delete_many({"net_id" : net_id})
            collection.insert_one(new_student_with_net_id(net_id))
        return True
    except Exception as e:
        logging.error('Failed to insert new student to MongoDB Cluster. Error: %s', str(e))
        return False
    
def delete_student_by_netid(net_id):
    """
    Deletes any student document from the
    students collection with the given netid.

    Parameters:
        net_id (str): NetID of student, like "kgwilson2"

    Returns:
        True (bool): if deletion is successful or netid not found
        False (bool): if operation fails
    """
    try:
        with connect() as client:
            collection = client[DB_NAME][COLLECTION_NAME]
            collection.delete_many({"net_id" : net_id})
        return True
    except Exception as e:
        logging.error('Failed to insert new student to MongoDB Cluster. Error: %s', str(e))
        return False

def update_ld_test_version(netid, proj_num, ld_used):
    """
    Setup for testing the update_late_days function.
    Deletes the student if it already exists in the ld
    collection.

    Parameters:
        netid (str): student whose late days should be updated
        proj_num (int): index of project to update, i.e. 3 for P3
        ld_used (int): number of late days used for project
    
    Returns:
        late_days (dict) or None: result of update_late_days function
    """
    delete_student_by_netid(netid)
    return update_late_days(netid, proj_num, ld_used)

def update_late_days(netid, proj_num, ld_used):
    """
    This function is as it appears in the docker_test component
    and as it appears in our hidden tests system.
    Creates a connection to the MongoDB cluster and updates
    the student's late days with a backoff strategy.
    With a maxPoolSize of 399, the maximum number of concurrent 
    connections that can be established to the MongoDB cluster 
    is limited to 399. This ensures that the number of connections
    does not exceed the limit of 500 and does not generate a warning
    (which occurs at 80% of max connections). This helps prevent connection 
    errors or performance degradation. When the function no longer
    needs the connection, it closes it, returning it to the pool.
    Short timeout (5 sec) helps reduce load on the cluster too.

    Parameters:
        netid (str): student whose late days should be updated
        proj_num (int): index of project to update, i.e. 3 for P3
        ld_used (int): number of late days used for project

    Returns:
        late_days (dict): late days dictionary where keys are project
                numbers as strings and values are late days used as ints
                (note that late days can be recorded past 12 total.)
                {
                    '3': 1,
                    '7': 3
                }
        None: if operation fails
    """
    
    max_attempts = 15
    filter_query = {"net_id": netid}
    update_query = {
        "$set": {f"late_days.{proj_num}": ld_used}
    }
    options = {
        "upsert": True,
        "return_document": ReturnDocument.AFTER
    }
    for _ in range(max_attempts):
        time.sleep(random.uniform(1,7))
        try:
            client = MongoClient(
                URI,
                ssl=True,
                tls=True,
                tlsAllowInvalidCertificates=True,
                maxPoolSize=399,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
            )
            collection = client[DB_NAME][COLLECTION_NAME]
            result = collection.find_one_and_update(
                filter_query,
                update_query,
                **options
            )
            return result.get("late_days") if result else None
        except Exception as e:
            print(e)
            if client:
                client.close()
            continue                
    print('Failed to connect to MongoDB Cluster and update late days.')
    return None
