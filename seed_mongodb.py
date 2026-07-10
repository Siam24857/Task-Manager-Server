#!/usr/bin/env python
"""
Script to seed MongoDB with fake task data
"""
import os
import sys
from datetime import datetime, timedelta
import random
from pymongo import MongoClient

# MongoDB configuration
MONGODB_URI = "mongodb+srv://Taskmanegr:s3NdVNE8RdxycZuN@cluster0.6ezfogq.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "taskmaneger"

# Fake task data
# Default user_id for seeded tasks (first registered user)
DEFAULT_USER_ID = 1
DEFAULT_USER_EMAIL = "demo@example.com"

fake_tasks = [
    {
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the task manager project including API endpoints, setup instructions, and user guide.",
        "status": "in_progress",
        "priority": "high",
        "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
        "tags": ["documentation", "priority"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Fix authentication bug",
        "description": "Users are experiencing issues with JWT token refresh. Need to investigate and fix the token rotation mechanism.",
        "status": "todo",
        "priority": "high",
        "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        "tags": ["bug", "authentication", "urgent"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Implement dark mode",
        "description": "Add dark mode toggle to the frontend application with proper theme persistence.",
        "status": "todo",
        "priority": "medium",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "tags": ["frontend", "ui", "feature"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Optimize database queries",
        "description": "Review and optimize slow database queries. Add proper indexing where needed.",
        "status": "in_progress",
        "priority": "medium",
        "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
        "tags": ["backend", "performance", "database"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Add unit tests",
        "description": "Write comprehensive unit tests for authentication and task management modules.",
        "status": "todo",
        "priority": "medium",
        "due_date": (datetime.now() + timedelta(days=10)).isoformat(),
        "tags": ["testing", "quality"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Deploy to production",
        "description": "Prepare and deploy the application to production environment with proper monitoring.",
        "status": "todo",
        "priority": "high",
        "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
        "tags": ["deployment", "production"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Review security implementation",
        "description": "Conduct security audit of the application including CORS, CSRF, and authentication mechanisms.",
        "status": "done",
        "priority": "high",
        "due_date": (datetime.now() - timedelta(days=2)).isoformat(),
        "tags": ["security", "audit"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Setup CI/CD pipeline",
        "description": "Configure automated testing and deployment pipeline using GitHub Actions.",
        "status": "in_progress",
        "priority": "medium",
        "due_date": (datetime.now() + timedelta(days=4)).isoformat(),
        "tags": ["devops", "automation"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Create user dashboard",
        "description": "Design and implement a user-friendly dashboard showing task statistics and progress.",
        "status": "todo",
        "priority": "low",
        "due_date": (datetime.now() + timedelta(days=21)).isoformat(),
        "tags": ["frontend", "dashboard", "ui"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    },
    {
        "title": "Add email notifications",
        "description": "Implement email notification system for task reminders and deadline alerts.",
        "status": "todo",
        "priority": "low",
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "tags": ["feature", "notifications"],
        "user_id": DEFAULT_USER_ID,
        "user_email": DEFAULT_USER_EMAIL,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
]

def seed_mongodb():
    """Connect to MongoDB and insert fake task data"""
    try:
        print(f"Connecting to MongoDB at {DATABASE_NAME}...")
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Check if tasks collection exists
        collections = db.list_collection_names()
        print(f"Existing collections: {collections}")
        
        # Use 'tasks' collection
        tasks_collection = db['tasks']
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing tasks...")
        tasks_collection.delete_many({})
        
        # Insert fake tasks
        print(f"Inserting {len(fake_tasks)} fake tasks...")
        result = tasks_collection.insert_many(fake_tasks)
        
        print(f"✅ Successfully inserted {len(result.inserted_ids)} tasks into MongoDB")
        print(f"Task IDs: {result.inserted_ids}")
        
        # Verify insertion
        count = tasks_collection.count_documents({})
        print(f"Total tasks in database: {count}")
        
        # Show sample task
        sample = tasks_collection.find_one()
        print(f"\nSample task:")
        print(f"  Title: {sample['title']}")
        print(f"  Status: {sample['status']}")
        print(f"  Priority: {sample['priority']}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error seeding MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Seeding Script")
    print("=" * 60)
    
    success = seed_mongodb()
    
    print("=" * 60)
    if success:
        print("Seeding completed successfully!")
        sys.exit(0)
    else:
        print("Seeding failed!")
        sys.exit(1)
