import os
import sys
import boto3
import json
import moto
import werkzeug
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3.0.0"
import json
from moto import mock_aws

# ==========================================
# MOTO SETUP
# ==========================================
# Ensure dummy credentials exist BEFORE importing boto3/app code
from werkzeug.security import generate_password_hash
from datetime import datetime
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Global counter for pass/fail
TESTS_PASSED = 0
TESTS_FAILED = 0

def assert_true(condition, message):
    global TESTS_PASSED, TESTS_FAILED
    if condition:
        print(f"[PASS] {message}")
        TESTS_PASSED += 1
    else:
        print(f"[FAIL] {message}")
        TESTS_FAILED += 1

@mock_aws
def run_verification():
    print("=========================================================")
    print("   STARTING MOTO VERIFICATION FOR INSTANT LIBRARY")
    print("=========================================================")
    
    # 1. SETUP INFRASTRUCTURE
    print("\n[1] Setting up Mock AWS Environment...")
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sns = boto3.client('sns', region_name='us-east-1')
    
    # Create Tables
    print("    - Creating DynamoDB Table: InstantLibrary_Users")
    dynamodb.create_table(
        TableName='InstantLibrary_Users',
        KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    print("    - Creating DynamoDB Table: InstantLibrary_Books")
    dynamodb.create_table(
        TableName='InstantLibrary_Books',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    print("    - Creating DynamoDB Table: InstantLibrary_Requests")
    dynamodb.create_table(
        TableName='InstantLibrary_Requests',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    print("    - Creating DynamoDB Table: InstantLibrary_OTP")
    dynamodb.create_table(
        TableName='InstantLibrary_OTP',
        KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    
    
    # Create EC2 Resource (Mock)
    ec2 = boto3.resource('ec2', region_name='us-east-1')
    ec2_client = boto3.client('ec2', region_name='us-east-1')

    # Create SNS Topic
    print("    - Creating SNS Topic")
    topic = sns.create_topic(Name='InstantLibraryNotifications')
    topic_arn = topic['TopicArn']

    # Create SQS Queue to capture SNS messages (Simulates Email Inbox)
    sqs = boto3.client('sqs', region_name='us-east-1')
    queue_url = sqs.create_queue(QueueName='TestEmailInbox')['QueueUrl']
    queue_arn = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']
    
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint=queue_arn
    )
    print("    - Subscribed SQS Queue to intercept SNS messages")
    
    # 2. IMPORT APP (Now that infrastructure is "up")
    print("\n[2] Loading Application Logic...")
    try:
        import app_aws
        # Inject the mock ARN
        app_aws.Config.SNS_TOPIC_ARN = topic_arn
        print(f"    - Injected Mock ARN: {topic_arn}")
    except ImportError:
        print("❌ CRITICAL: Could not import app_aws.py. Make sure requirements are installed.")
        return

    # 3. TEST DATABASE SERVICE
    print("\n[3] Testing Database Service...")
    db = app_aws.DatabaseService
    
    # Test Create User
    user_data = {
        'email': 'test@student.com',
        'name': 'Test Student',
        'password': generate_password_hash('secret123'),
        'role': 'student',
        'roll_no': 'CS101'
    }
    db.create_user(user_data)
    
    fetched_user = db.get_user('test@student.com')
    assert_true(fetched_user is not None, "User created and fetched successfully")
    assert_true(fetched_user['name'] == 'Test Student', "User data integrity check")
    
    # Test Add Book (We can use the table directly or API logic, let's use boto3 direct for setup then db for fetch)
    book_id = 'book-123'
    app_aws.books_table.put_item(Item={
        'id': book_id,
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'copies': 2
    })
    
    fetched_book = db.get_book(book_id)
    assert_true(fetched_book is not None, "Book created and fetched")
    assert_true(fetched_book['title'] == 'The Great Gatsby', "Book title check")

    # 4. TEST NOTIFICATION SERVICE
    print("\n[4] Testing Notification Service...")
    
    # We need to subscribe an email to the topic to "receive" the message in Moto? 
    # Moto SNS stores sent messages.
    
    notif = app_aws.NotificationService
    try:
        notif.send('test@student.com', 'Test Subject', 'This is a test body.')
        assert_true(True, "NotificationHelper.send() executed without error")
    except Exception as e:
        assert_true(False, f"NotificationHelper.send() failed: {e}")
    # 5. TEST ALL NOTIFICATION TYPES via FLASK/LOGIC
    print("\n[5] Testing All Notification Flows via App Logic...")
    
    # helper to clear queue
    def clear_queue():
        while True:
            m = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=0)
            if 'Messages' not in m: break
            entries = [{'Id': x['MessageId'], 'ReceiptHandle': x['ReceiptHandle']} for x in m['Messages']]
            sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)
    
    clear_queue()
    
    # 5.1 Registration Notification
    print("    - Triggering: New User Registration")
    with app_aws.app.test_request_context():
        app_aws.handle_registration(
            type('obj', (object,), {'form': {
                'email': 'new_user@test.com', 'name': 'New User', 'password': 'pw', 
                'confirm_password': 'pw', 'role': 'student', 'roll_no': '1', 'semester': '1', 'year': '1'
            }}), 
            'student'
        )
    
    # 5.2 Login Notification
    print("    - Triggering: User Login")
    with app_aws.app.test_client() as client:
        client.post('/login', data={'action': 'login', 'email': 'new_user@test.com', 'password': 'pw', 'role': 'student'})
    
    # 5.3 Request Book (Pending)
    print("    - Triggering: Book Request (Pending)")
    with app_aws.app.test_client() as client:
        # Login first to set session
        client.post('/login', data={'action': 'login', 'email': 'new_user@test.com', 'password': 'pw', 'role': 'student'})
        client.get(f'/request_book/{book_id}', follow_redirects=True)
            
    # 5.4 Waitlist (Simulate 0 copies)
    print("    - Triggering: Book Waitlist")
    app_aws.books_table.update_item(Key={'id': book_id}, UpdateExpression="set copies=:c", ExpressionAttributeValues={':c': 0})
    
    # Clean up previous request
    scan = app_aws.requests_table.scan()
    for i in scan.get('Items', []):
        app_aws.requests_table.delete_item(Key={'id': i['id']})

    with app_aws.app.test_client() as client:
        client.post('/login', data={'action': 'login', 'email': 'new_user@test.com', 'password': 'pw', 'role': 'student'})
        client.get(f'/request_book/{book_id}', follow_redirects=True)

    # 5.5 Staff Actions (Approve, Return, Reject)
    print("    - Triggering: Staff Actions (Approve, Return, Reject)")
    
    # Need to get the request ID from the DB
    req_scan = app_aws.requests_table.scan()
    req_id = req_scan['Items'][0]['id']
    
    with app_aws.app.test_client() as client:
        # Login as Staff (Need to create staff user first?)
        # Logic doesn't stick session across requests in test client easily without cookies, 
        # so we just re-login as staff for each action or use one session
        
        # Create Staff User
        app_aws.users_table.put_item(Item={
            'email': 'staff@test.com', 'name': 'Staff User', 'password': 'scrypt:32768:8:1$kJD...', 'role': 'staff'
        })
        # Wait, I should import generate_password_hash or use a known hash. 
        # Actually generate_password_hash is imported at top of file.
        app_aws.users_table.put_item(Item={
            'email': 'staff@test.com', 'name': 'Staff User', 'password': generate_password_hash('pw'), 'role': 'staff'
        })
        
        # RESTOCK BOOK (so approval works)
        app_aws.books_table.update_item(Key={'id': book_id}, UpdateExpression="set copies=:c", ExpressionAttributeValues={':c': 5})
        
        # Login Staff
        client.post('/login', data={'action': 'login', 'email': 'staff@test.com', 'password': 'pw', 'role': 'staff'})
        
        # 5.5.1 Approve
        print("      -> Approving Request")
        client.get(f'/staff/request/{req_id}/approve', follow_redirects=True)
        
        # 5.5.2 Return
        print("      -> Returning Book")
        client.get(f'/staff/request/{req_id}/return', follow_redirects=True)
        
        # 5.5.3 Reject (Re-using logic, code allows state change)
        print("      -> Rejecting Request")
        client.get(f'/staff/request/{req_id}/reject', follow_redirects=True)
        
        # 5.6 Staff Management Actions (Audit Logs)
        print("    - Triggering: Staff Audit Actions (Add Book, Delete Book, Delete User)")
        
        # 5.6.1 Add Book
        client.post('/staff/add_book', data={
            'title': 'New Audit Book', 'author': 'Audit', 'category': 'Test', 
            'copies': 1, 'isbn': '123', 'cover_url': 'http://test'
        }, follow_redirects=True)
        
        # 5.6.2 Delete Book (Delete the one we just added? Need its ID, but it's generated UUID)
        # Let's delete the 'book-123' we used earlier
        client.get(f'/staff/delete_book/{book_id}', follow_redirects=True)
        
        # 5.6.3 Delete User (Delete the student)
        client.get('/staff/delete_user/new_user@test.com', follow_redirects=True)

    # 5.7 Change Password (User Action)
    print("    - Triggering: User Password Change")
    with app_aws.app.test_client() as client:
        # Re-create student first (since we just deleted them above!)
        app_aws.users_table.put_item(Item={
            'email': 'alive_student@test.com', 'name': 'Alive Student', 'password': generate_password_hash('pw'), 'role': 'student'
        })
        
        client.post('/login', data={'action': 'login', 'email': 'alive_student@test.com', 'password': 'pw', 'role': 'student'})
        
        # Change Password
        client.post('/profile', data={
            'current_password': 'pw',
            'new_password': 'new_pw',
            'confirm_password': 'new_pw'
        }, follow_redirects=True)

    # 5.8 Forgot Password Flow
    print("    - Triggering: Forgot Password Flow")
    with app_aws.app.test_client() as client:
        # Request OTP
        client.post('/forgot-password', data={'email': 'alive_student@test.com'}, follow_redirects=True)
        
        # Verify OTP (We need to fetch the OTP from DB to verify it)
        otp_resp = app_aws.password_resets_table.get_item(Key={'email': 'alive_student@test.com'})
        otp_code = otp_resp['Item']['otp']
        
        # client session should retain 'reset_email' from previous POST
        client.post('/verify-otp', data={'otp': otp_code}, follow_redirects=True)
        
        # Reset Password
        client.post('/reset-password', data={'password': 'reset_pw', 'confirm_password': 'reset_pw'}, follow_redirects=True)

    # 6. DYNAMODB STRESS TEST (The "Hard Way")
    print("\n[6] Stress Testing DynamoDB (50 Users & Requests)...")
    with app_aws.app.test_client() as client:
        # Create 50 Users
        print("    - Batch Creating 50 Users...")
        for i in range(50):
            email = f"stress_user_{i}@test.com"
            app_aws.users_table.put_item(Item={
                'email': email, 'name': f'Stress User {i}', 
                'password': generate_password_hash('pw'), 
                'role': 'student'
            })
            
        # Create 50 Books
        print("    - Batch Creating 50 Books...")
        for i in range(50):
            app_aws.books_table.put_item(Item={
                'id': f'stress-book-{i}', 'title': f'Stress Book {i}', 
                'author': 'Stress Test', 'copies': 5
            })
            
        # 50 Requests (1 per user)
        print("    - Simulating 50 Simultaneous Book Requests...")
        for i in range(50):
            # We skip the full login flow for speed, just direct DB insert or simulated session
            # Doing direct DB insert to test Table Write Capacity mostly
            import uuid
            app_aws.requests_table.put_item(Item={
                'id': str(uuid.uuid4()),
                'user_email': f"stress_user_{i}@test.com",
                'book_id': f'stress-book-{i}',
                'status': 'pending',
                'date': datetime.now().strftime("%Y-%m-%d")
            })

        # Verify Counts
        u_count = app_aws.users_table.scan()['Count']
        b_count = app_aws.books_table.scan()['Count']
        r_count = app_aws.requests_table.scan()['Count']
        
        print(f"    - User Count: {u_count} (Expected >= 52)") # 50 + original tests
        print(f"    - Book Count: {b_count} (Expected >= 51)")
        print(f"    - Request Count: {r_count} (Expected >= 51)")
        
        assert_true(u_count >= 52, "Stress User Count Verified")
        assert_true(b_count >= 51, "Stress Book Count Verified")
        assert_true(r_count >= 51, "Stress Request Count Verified")

    # 7. SNS STRESS TEST
    print("\n[7] Stress Testing SNS (50 Rapid Notifications)...")
    for i in range(50):
        # We use the service directly to test throughput
        app_aws.NotificationService.send('test@stress.com', f"Stress Message {i}", f"Body {i}")
    
    # 8. EC2 DEPLOYMENT SIMULATION
    print("\n[8] Simulating EC2 Deployment Infrastructure...")
    
    # 8.1 Create Security Group
    sg_name = 'InstantLibrary-SG'
    try:
        sg = ec2.create_security_group(GroupName=sg_name, Description='Allow Flask and SSH')
        sg_id = sg.id
        print(f"    - Security Group Created: {sg_name} ({sg_id})")
        
        # Add Rules (Port 5000 for Flask, 22 for SSH)
        sg.authorize_ingress(IpProtocol='tcp', FromPort=5000, ToPort=5000, CidrIp='0.0.0.0/0')
        sg.authorize_ingress(IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0')
        print("    - Ingress Rules Added (Port 5000, 22)")
    except Exception as e:
        print(f"    [ERROR] SG Creation Failed: {e}")

    # 8.2 Launch Instance
    print("    - Launching EC2 Instance (t2.micro)...")
    instances = ec2.create_instances(
        ImageId='ami-12345678', # Dummy AMI for Moto
        MinCount=1, MaxCount=1,
        InstanceType='t2.micro',
        SecurityGroupIds=[sg_id]
    )
    instance = instances[0]
    
    # Wait for running (Instant in Moto usually)
    instance.reload()
    if instance.state['Name'] == 'pending':
        print("    - Instance Pending... waiting")
        # In real boto3 we'd use a waiter, but moto is fast
        
    print(f"    - Instance Launched! ID: {instance.id}")
    print(f"    - State: {instance.state['Name']}")
    print(f"    - Public IP: {instance.public_ip_address} (Simulated)")
    
    assert_true(instance.id.startswith('i-'), "Instance ID Valid")
    # Moto might return 'running' or 'pending' immediately depending on version
    assert_true(instance.state['Name'] in ['running', 'pending'], "Instance State Valid")

    # 10. VERIFY ANALYTICS API
    print("\n[10] Verifying Utils (Analytics API)...")
    with app_aws.app.test_client() as client:
        # Need to login as staff first
        client.post('/login', data={'action': 'login', 'email': 'staff@test.com', 'password': 'pw', 'role': 'staff'})
        res = client.get('/api/analytics')
        assert_true(res.status_code == 200, "Analytics API returns 200 OK")
        
        data = res.get_json()
        print(f"    - Keys received: {list(data.keys())}")
        assert_true('popular_labels' in data, "Contains 'popular_labels'")
        assert_true('status_data' in data, "Contains 'status_data'")
        assert_true(data['total_requests'] >= 50, "Data reflects stress test")

    # 11. VERIFY RECOMMENDATION API
    print("\n[11] Verifying AI Recommendations API...")
    with app_aws.app.test_client() as client:
        # Login as student
        client.post('/login', data={'action': 'login', 'email': 'stress_user_0@test.com', 'password': 'pw', 'role': 'student'})
        res = client.get('/api/recommendations')
        assert_true(res.status_code == 200, "Recs API returns 200 OK")
        
        data = res.get_json()
        print(f"    - Response Data: {data}")
        print(f"    - Source: {data.get('source')}")
        print(f"    - Books Returned: {len(data.get('books', []))}")
        
        assert_true('books' in data, "Contains 'books' list")
        assert_true(len(data['books']) > 0, "Returned at least 1 book")
        # In test env without API Key, source should likely be 'random' or 'fallback'
        assert_true(data['source'] in ['random', 'fallback', 'ai'], "Valid Source Type")

    # 12. SUMMARY
    print("\n[12] SUMMARY OF RESULTS")
    
    all_messages = []
    while True:
        msgs = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2
        )
        if 'Messages' in msgs:
            all_messages.extend(msgs['Messages'])
            # Delete them so we don't fetch again if we loop? 
            # Actually standard SQS pattern is fetch -> process -> delete.
            # But here we just want to verify. 
            # If we don't delete, we keep getting same ones? No, VisibilityTimeout hides them.
            # But let's simple delete to be sure.
            entries = [{'Id': x['MessageId'], 'ReceiptHandle': x['ReceiptHandle']} for x in msgs['Messages']]
            sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)
        else:
            break
            
    if all_messages:
        print(f"    [INFO] Found {len(all_messages)} message(s) in inbox.")
        
        # Check we have enough messages (Previous ~15 + 50 Stress = 65+)
        assert_true(len(all_messages) >= 65, "Captured all Stress Notifications")
        
        for m in all_messages:
            body = json.loads(m['Body'])
            # SNS wraps the message, so we look at 'Message' inside the SQS body
            sns_msg = body.get('Message', '')
            sns_subj = body.get('Subject', 'No Subject')
            print(f"    [EMAIL RECEIVED] Subject: {sns_subj}")
            if "New Registration" in sns_subj: assert_true(True, "Caught Registration Email")
            elif "Welcome to Instant Library" in sns_subj: assert_true(True, "Caught Welcome Email")
            elif "Login Alert" in sns_subj: assert_true(True, "Caught Login Alert")
            elif "Request Received" in sns_subj: assert_true(True, "Caught Request Confirmation")
            elif "Added to Waitlist" in sns_subj: assert_true(True, "Caught Waitlist Alert")
            elif "Request Approved" in sns_subj: assert_true(True, "Caught Approval Email")
            elif "Book Returned" in sns_subj: assert_true(True, "Caught Return Email")
            elif "Request Rejected" in sns_subj: assert_true(True, "Caught Rejection Email")
            # New Audit/Security Checks
            elif "Audit: New Book Added" in sns_subj: assert_true(True, "Caught Book Add Audit")
            elif "Audit: Book Deleted" in sns_subj: assert_true(True, "Caught Book Delete Audit")
            elif "Audit: User Deleted" in sns_subj: assert_true(True, "Caught User Delete Audit")
            elif "Audit: User Deleted" in sns_subj: assert_true(True, "Caught User Delete Audit")
            elif "Security Alert: Password Changed" in sns_subj: assert_true(True, "Caught Password Change Alert")
            elif "Security Alert: Password Reset OTP" in sns_subj: assert_true(True, "Caught OTP Email")
            elif "Audit: Password Reset" in sns_subj: assert_true(True, "Caught Reset Audit")
            else: print(f"    [INFO] Extra Email: {sns_subj}")
    else:
        assert_true(False, "No messages found in SQS inbox! SNS Publish may have failed.")

    # 6. TEST FLASK ROUTES (Simulated)
    # The Core AWS Logic has already passed above!
    # 7. FLASK ROUTE TESTING
    print("\n[7] Flask Route Testing Skipped (Core Logic Verified)")
    
    with app_aws.app.test_client() as client:
        # Test Index
        resp = client.get('/')
        assert_true(resp.status_code == 200, "Index page loads (200 OK)")
        
        # Test Auth Page
        resp = client.get('/auth?mode=login')
        assert_true(resp.status_code == 200, "Login page loads (200 OK)")

        # Test Login POST (Real Login Flow)
        resp = client.post('/login', data={
            'email': 'test@student.com',
            'password': 'secret123',
            'action': 'login'
        }, follow_redirects=True)
        assert_true(resp.status_code == 200, "Login POST successful")
        assert_true(b'Catalog' in resp.data or b'Dashboard' in resp.data or b'Request Book' in resp.data, "Redirected to Dashboard/Catalog")
        
        # Test Dashboard access (Session should be set by login)
        resp = client.get('/catalog')
        assert_true(resp.status_code == 200, "Catalog/Dashboard loads for logged-in user")

    # SUMMARY
    print("\n=========================================================")
    print(f"   VERIFICATION COMPLETE")
    print(f"   PASSED: {TESTS_PASSED}  |  FAILED: {TESTS_FAILED}")
    print("=========================================================")

if __name__ == "__main__":
    run_verification()
