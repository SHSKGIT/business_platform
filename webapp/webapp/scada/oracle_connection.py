import os
import environ

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

import cx_Oracle
from django.conf import settings


def oracle_connection():
    cx_Oracle.init_oracle_client(lib_dir=env("LD_LIBRARY_PATH"))
    # Establish a connection to the Oracle database
    dsn = cx_Oracle.makedsn(
        settings.DATABASES["oracle"]["HOST"],
        settings.DATABASES["oracle"]["PORT"],
        service_name=settings.DATABASES["oracle"]["NAME"],
    )
    connection = cx_Oracle.connect(
        settings.DATABASES["oracle"]["USER"],
        settings.DATABASES["oracle"]["PASSWORD"],
        dsn,
    )

    return connection


def fetch_one_from_oracle(query):
    connection = oracle_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)
        return cursor.fetchone()  # Fetch only one result
    finally:
        cursor.close()
        connection.close()


def fetch_all_from_oracle(query):
    connection = oracle_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)
        return cursor.fetchall()  # Fetch all results
    finally:
        cursor.close()
        connection.close()


def update_data_in_oracle(query):
    connection = oracle_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)  # Execute the update query
        connection.commit()  # Commit the transaction to save changes
    except cx_Oracle.DatabaseError as e:
        print("Error occurred during the update: ", e)
        connection.rollback()  # Rollback in case of error
    finally:
        cursor.close()
        connection.close()


def insert_data_into_oracle(query):
    connection = oracle_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)  # Execute the insert query
        connection.commit()  # Commit the transaction to save changes
    except cx_Oracle.DatabaseError as e:
        print("Error occurred during the insert:", e)
        connection.rollback()  # Rollback in case of error
    finally:
        cursor.close()
        connection.close()


def delete_data_from_oracle(query):
    connection = oracle_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)  # Execute the delete query
        connection.commit()  # Commit the transaction to save changes
    except cx_Oracle.DatabaseError as e:
        print("Error occurred during the delete:", e)
        connection.rollback()  # Rollback in case of error
    finally:
        cursor.close()
        connection.close()
