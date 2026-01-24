import boto3
import time

def setup_dynamodb():
    # Configure AWS region
    AWS_REGION = 'us-east-1' # Ensure this matches your AWS_app.py config
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    
    tables = [
        {
            'TableName': 'InstantLibrary_Users',
            'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'email', 'AttributeType': 'S'}]
        },
        {
            'TableName': 'InstantLibrary_Books',
            'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}]
        },
        {
            'TableName': 'InstantLibrary_Requests',
            'KeySchema': [{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'request_id', 'AttributeType': 'S'}]
        },
        {
            'TableName': 'InstantLibrary_Notifications',
            'KeySchema': [{'AttributeName': 'id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'id', 'AttributeType': 'S'}]
        },
        {
            'TableName': 'InstantLibrary_OTP',
            'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'email', 'AttributeType': 'S'}],
            'TTL': {'AttributeName': 'ttl', 'Enabled': True}
        }
    ]
    
    print("⏳ Starting DynamoDB Table Creation...")
    
    existing_tables = [t.name for t in dynamodb.tables.all()]
    
    for table_config in tables:
        table_name = table_config['TableName']
        
        if table_name in existing_tables:
            print(f"⚠️  Table {table_name} already exists. Skipping.")
            continue
            
        print(f"🔨 Creating table: {table_name}...")
        
        try:
            params = {
                'TableName': table_name,
                'KeySchema': table_config['KeySchema'],
                'AttributeDefinitions': table_config['AttributeDefinitions'],
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
            
            table = dynamodb.create_table(**params)
            
            # Enable TTL for OTP table if configured
            if 'TTL' in table_config:
                print(f"   Waiting for {table_name} to be active to enable TTL...")
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                
                dynamodb.Table(table_name).update_time_to_live(
                    TimeToLiveSpecification={
                        'Enabled': True,
                        'AttributeName': table_config['TTL']['AttributeName']
                    }
                )
                print(f"   ✅ TTL enabled for {table_name}")
                
            print(f"✅ Created {table_name}")
            
        except Exception as e:
            print(f"❌ Failed to create {table_name}: {e}")
            
    print("\n🎉 DynamoDB setup complete!")

if __name__ == '__main__':
    setup_dynamodb()
