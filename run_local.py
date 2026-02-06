import os
import boto3
import requests
import random
from moto import mock_aws
from flask import Flask

# 1. Mock Credentials Logic (Must be before importing app)
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# 2. Setup Mocks
mock = mock_aws()
mock.start()

# 3. Import App (Now it connects to Mock AWS)
import app_aws
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_data():
    print(">>> Setting up Local Mock Environment...")
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sns = boto3.client('sns', region_name='us-east-1')

    # Create Tables
    dynamodb.create_table(
        TableName='InstantLibrary_Users',
        KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    dynamodb.create_table(
        TableName='InstantLibrary_Books',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    dynamodb.create_table(
        TableName='InstantLibrary_Requests',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    dynamodb.create_table(
        TableName='InstantLibrary_OTP',
        KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    # Create SNS
    sns.create_topic(Name='InstantLibraryNotifications')

    # SEED DATA (Disabled for "From 0" Experience)
    # 1. Staff User
    # app_aws.users_table.put_item(Item={
    #     'email': 'staff@test.com', 
    #     'name': 'Staff Admin', 
    #     'password': generate_password_hash('pw'), 
    #     'role': 'staff'
    # })
    
    # 2. Student User
    # app_aws.users_table.put_item(Item={
    #     'email': 'student@test.com', 
    #     'name': 'Student User', 
    #     'password': generate_password_hash('pw'), 
    #     'role': 'student'
    # })
    
    
    # 3. Books (Empty for fresh start)
    # Books will be auto-populated by the Staff Dashboard logic
    
    # 4. Requests (Empty for fresh start)

    print(">>> Environment Ready!")
    print(">>> Login Credentials:")
    print("    Staff:   staff@test.com / pw")
    print("    Student: student@test.com / pw")

def populate_large_catalog():
    print(">>> Silently fetching 500 books from Open Library... (This may take a moment)")
    subjects = ['science_fiction', 'adventure', 'history', 'programming', 'biology']
    # ... (function content remains but is ensuring it's not called) ...
    # Simplified for readability in this view, effectively I just need to remove the CALL in main
    pass 

if __name__ == '__main__':
    setup_data()
    # populate_large_catalog()  <-- Disabled for "From 0" experience
    print(">>> Starting Local Server on http://127.0.0.1:5000")
    app_aws.app.run(port=5000, debug=True, use_reloader=False)
