#!/usr/bin/env python
"""
Script to create fake users in Django database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Fake users data
fake_users = [
    {
        'email': 'john.doe@example.com',
        'username': 'johndoe',
        'password': 'Test123456!',
        'first_name': 'John',
        'last_name': 'Doe'
    },
    {
        'email': 'jane.smith@example.com',
        'username': 'janesmith',
        'password': 'Test123456!',
        'first_name': 'Jane',
        'last_name': 'Smith'
    },
    {
        'email': 'admin@example.com',
        'username': 'admin',
        'password': 'Admin123456!',
        'first_name': 'Admin',
        'last_name': 'User'
    },
    {
        'email': 'developer@example.com',
        'username': 'developer',
        'password': 'Dev123456!',
        'first_name': 'Dev',
        'last_name': 'Coder'
    },
    {
        'email': 'tester@example.com',
        'username': 'tester',
        'password': 'Test123456!',
        'first_name': 'Test',
        'last_name': 'User'
    }
]

def seed_users():
    """Create fake users in Django database"""
    print("=" * 60)
    print("Django User Seeding Script")
    print("=" * 60)
    
    created_users = []
    
    for user_data in fake_users:
        email = user_data['email']
        username = user_data['username']
        password = user_data['password']
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            print(f"⚠️  User {email} already exists, skipping...")
            continue
        
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            created_users.append(user)
            print(f"✅ Created user: {email}")
        except Exception as e:
            print(f"❌ Error creating user {email}: {str(e)}")
    
    print("=" * 60)
    print(f"Successfully created {len(created_users)} users")
    print("=" * 60)
    
    if created_users:
        print("\n📋 User Credentials:")
        print("-" * 60)
        for i, user_data in enumerate(fake_users, 1):
            print(f"\n{i}. Email: {user_data['email']}")
            print(f"   Username: {user_data['username']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
        print("-" * 60)
    
    return len(created_users) > 0

if __name__ == "__main__":
    success = seed_users()
    sys.exit(0 if success else 1)
