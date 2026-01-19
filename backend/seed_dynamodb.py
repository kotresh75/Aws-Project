import boto3
import time
from datetime import datetime
import hashlib

# ==================== CONFIGURATION ====================
REGION = 'us-east-1'  # Change to your AWS Region
DYNAMODB_ENDPOINT = None # set to 'http://localhost:8000' for local dynamo
# =======================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def seed_data():
    print(f"🌱 Connecting to DynamoDB in {REGION}...")
    dynamodb = boto3.resource('dynamodb', region_name=REGION)

    # ==================== 1. SEED BOOKS ====================
    try:
        table = dynamodb.Table('Books')
        print(f"📚 Seeding 'Books' table...")
        
        books_data = [
            {
                "id": 1, 
                "title": "Introduction to Algorithms", 
                "author": "Thomas H. Cormen", 
                "subject": "Computer Science", 
                "description": "A comprehensive guide to algorithms and data structures", 
                "year": 2009, 
                "available_count": 3, 
                "total_count": 5, 
                "isbn": "978-0262033848",
                "cover_image": "https://m.media-amazon.com/images/I/41SNoh5ZhOL._SY264_BO1,204,203,200_QL40_ML2_.jpg",
                "copies": ["978-0262033848-001", "978-0262033848-002", "978-0262033848-003", "978-0262033848-004", "978-0262033848-005"],
                "pdf_url": "https://example.com/algorithms.pdf"
            },
            {
                "id": 2, 
                "title": "Data Science Handbook", 
                "author": "Jake VanderPlas", 
                "subject": "Data Science", 
                "description": "A practical guide to data science with Python", 
                "year": 2016, 
                "available_count": 2, 
                "total_count": 3,
                "isbn": "978-1491912058",
                "cover_image": "https://m.media-amazon.com/images/I/516C1yC59fL._SX218_BO1,204,203,200_QL40_ML2_.jpg",
                "copies": ["978-1491912058-001", "978-1491912058-002", "978-1491912058-003"]
            },
            {
                "id": 3, 
                "title": "Web Development with Flask", 
                "author": "Miguel Grinberg", 
                "subject": "Web Development", 
                "description": "Learn web development using Flask framework", 
                "year": 2018, 
                "available_count": 0, 
                "total_count": 2,
                "isbn": "978-1491991732",
                "cover_image": "https://m.media-amazon.com/images/I/41w8B3w-CPL._SX379_BO1,204,203,200_.jpg",
                "copies": ["978-1491991732-001", "978-1491991732-002"]
            },
            {
                "id": 4, 
                "title": "Cloud Computing Basics", 
                "author": "Tom Bowers", 
                "subject": "Cloud Computing", 
                "description": "Introduction to cloud computing and AWS", 
                "year": 2020, 
                "available_count": 4, 
                "total_count": 4,
                "isbn": "978-1234567890",
                "cover_image": "https://m.media-amazon.com/images/I/41-s7S+wFPL._SY346_.jpg",
                "copies": ["978-1234567890-001", "978-1234567890-002", "978-1234567890-003", "978-1234567890-004"]
            },
            {
                "id": 5, 
                "title": "Database Design", 
                "author": "C.J. Date", 
                "subject": "Databases", 
                "description": "Best practices in database design and normalization", 
                "year": 2015, 
                "available_count": 1, 
                "total_count": 3,
                "isbn": "978-0321295359",
                "cover_image": "https://m.media-amazon.com/images/I/41+7+G+k06L._SL500_.jpg",
                "copies": ["978-0321295359-001", "978-0321295359-002", "978-0321295359-003"]
            },
            {
                "id": 6, 
                "title": "Python Programming", 
                "author": "Guido van Rossum", 
                "subject": "Programming", 
                "description": "Complete guide to Python programming language", 
                "year": 2021, 
                "available_count": 5, 
                "total_count": 5,
                "isbn": "978-0321200000",
                "cover_image": "https://m.media-amazon.com/images/I/41oGkQd3T3L._SX385_BO1,204,203,200_.jpg",
                "copies": ["978-0321200000-001", "978-0321200000-002", "978-0321200000-003", "978-0321200000-004", "978-0321200000-005"]
            },
            {
                "id": 7, 
                "title": "Machine Learning Basics", 
                "author": "Andrew Ng", 
                "subject": "Machine Learning", 
                "description": "Introduction to machine learning and AI", 
                "year": 2019, 
                "available_count": 2, 
                "total_count": 4,
                "isbn": "978-0321300000",
                "cover_image": "https://m.media-amazon.com/images/I/51w+S6u0VLL._SX379_BO1,204,203,200_.jpg",
                "copies": ["978-0321300000-001", "978-0321300000-002", "978-0321300000-003", "978-0321300000-004"]
            }
        ]
        
        with table.batch_writer() as batch:
            for book in books_data:
                batch.put_item(Item=book)
        print(f"✅ Successfully added {len(books_data)} books.")
        
    except Exception as e:
        print(f"❌ Error seeding Books: {e}")

    # ==================== 2. SEED USERS ====================
    try:
        table = dynamodb.Table('Users')
        print(f"👤 Seeding 'Users' table...")
        
        users_data = [
            {
                'email': 'staff@gmail.com',
                'password': hash_password('123456'),
                'name': 'Staff Member',
                'role': 'staff',
                'verified': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'email': 'student@gmail.com',
                'password': hash_password('123456'),
                'name': 'Student Member',
                'role': 'student',
                'roll_no': 'S101',
                'semester': '1',
                'year': '1',
                'verified': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'email': 'veerkotresh@gmail.com',
                'password': hash_password('123456'),
                'name': 'Veer Kotresh',
                'role': 'student',
                'roll_no': 'S102',
                'semester': '3',
                'year': '2',
                'verified': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'email': 'alice@example.com',
                'password': hash_password('123456'),
                'name': 'Alice Johnson',
                'role': 'student',
                'roll_no': 'S103',
                'semester': '5',
                'year': '3',
                'verified': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'email': 'bob@example.com',
                'password': hash_password('123456'),
                'name': 'Bob Smith',
                'role': 'student',
                'roll_no': 'S104',
                'semester': '7',
                'year': '4',
                'verified': True,
                'created_at': datetime.now().isoformat()
            }
        ]
        
        with table.batch_writer() as batch:
            for user in users_data:
                batch.put_item(Item=user)
        print(f"✅ Successfully added {len(users_data)} users.")
        
    except Exception as e:
        print(f"❌ Error seeding Users: {e}")

    print("\n✨ Database seeding complete!")

if __name__ == "__main__":
    seed_data()
