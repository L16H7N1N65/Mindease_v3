#!/usr/bin/env python3
"""
Database seeder script for MindEase API.
Creates minimal dummy data for testing and development.
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine
from app.db.models.auth import User, Role, Permission, Profile, Preference
from app.db.models.mood import MoodEntry, MoodFactor
from app.db.models.therapy import TherapySession, TherapyProgram
from app.db.models.organization import Organization
from app.core.security import get_password_hash


def create_dummy_data():
    """Create minimal dummy data for testing."""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Check if data already exists
        if db.query(User).count() > 0:
            print("⚠️  Database already contains users. Skipping seeding.")
            return
        
        # Create roles
        print("📝 Creating roles...")
        admin_role = Role(
            name="admin",
            description="Administrator with full access"
        )
        user_role = Role(
            name="user", 
            description="Regular user with basic access"
        )
        therapist_role = Role(
            name="therapist",
            description="Therapist with therapy management access"
        )
        
        db.add_all([admin_role, user_role, therapist_role])
        db.commit()
        
        # Create permissions for admin role
        print("🔐 Creating permissions...")
        admin_permissions = [
            Permission(role_id=admin_role.id, resource="users", can_create=True, can_read=True, can_update=True, can_delete=True),
            Permission(role_id=admin_role.id, resource="roles", can_create=True, can_read=True, can_update=True, can_delete=True),
            Permission(role_id=admin_role.id, resource="organizations", can_create=True, can_read=True, can_update=True, can_delete=True),
        ]
        
        user_permissions = [
            Permission(role_id=user_role.id, resource="mood_entries", can_create=True, can_read=True, can_update=True, can_delete=True),
            Permission(role_id=user_role.id, resource="therapy_sessions", can_create=True, can_read=True, can_update=True, can_delete=False),
            Permission(role_id=user_role.id, resource="social_posts", can_create=True, can_read=True, can_update=True, can_delete=True),
        ]
        
        db.add_all(admin_permissions + user_permissions)
        db.commit()
        
        # Create users
        print("👥 Creating users...")
        
        # Admin user
        admin_user = User(
            username="admin",
            email="admin@mindease.com",
            password_hash=get_password_hash("admin123"),
            is_active=True,
            email_confirmed=True,
            terms_accepted=True,
            terms_accepted_at=datetime.utcnow()
        )
        admin_user.roles.append(admin_role)
        
        # Regular user 1
        user1 = User(
            username="john_doe",
            email="john@example.com", 
            password_hash=get_password_hash("password123"),
            is_active=True,
            email_confirmed=True,
            terms_accepted=True,
            terms_accepted_at=datetime.utcnow()
        )
        user1.roles.append(user_role)
        
        # Regular user 2
        user2 = User(
            username="jane_smith",
            email="jane@example.com",
            password_hash=get_password_hash("password123"),
            is_active=True,
            email_confirmed=True,
            terms_accepted=True,
            terms_accepted_at=datetime.utcnow()
        )
        user2.roles.append(user_role)
        
        # Therapist user
        therapist = User(
            username="dr_wilson",
            email="therapist@mindease.com",
            password_hash=get_password_hash("therapist123"),
            is_active=True,
            email_confirmed=True,
            terms_accepted=True,
            terms_accepted_at=datetime.utcnow()
        )
        therapist.roles.append(therapist_role)
        
        db.add_all([admin_user, user1, user2, therapist])
        db.commit()
        
        # Create profiles
        print("👤 Creating user profiles...")
        profiles = [
            Profile(
                user_id=admin_user.id,
                first_name="Admin",
                last_name="User",
                bio="System administrator"
            ),
            Profile(
                user_id=user1.id,
                first_name="John",
                last_name="Doe",
                bio="Software developer interested in mental wellness"
            ),
            Profile(
                user_id=user2.id,
                first_name="Jane",
                last_name="Smith",
                bio="Teacher exploring mindfulness practices"
            ),
            Profile(
                user_id=therapist.id,
                first_name="Dr. Sarah",
                last_name="Wilson",
                bio="Licensed therapist specializing in anxiety and depression"
            )
        ]
        
        db.add_all(profiles)
        db.commit()
        
        # Create preferences
        print("⚙️  Creating user preferences...")
        preferences = [
            Preference(
                user_id=admin_user.id,
                theme="dark",
                language="en",
                notifications_enabled=True,
                email_notifications=True
            ),
            Preference(
                user_id=user1.id,
                theme="light",
                language="en",
                notifications_enabled=True,
                email_notifications=False
            ),
            Preference(
                user_id=user2.id,
                theme="light",
                language="en",
                notifications_enabled=True,
                email_notifications=True
            ),
            Preference(
                user_id=therapist.id,
                theme="light",
                language="en",
                notifications_enabled=True,
                email_notifications=True
            )
        ]
        
        db.add_all(preferences)
        db.commit()
        
        # Create sample mood entries
        print("😊 Creating sample mood entries...")
        base_date = datetime.utcnow() - timedelta(days=7)
        
        mood_entries = []
        for i in range(7):
            entry_date = base_date + timedelta(days=i)
            
            # Mood entry for user1
            mood1 = MoodEntry(
                user_id=user1.id,
                mood_score=7 + (i % 3),  # Varies between 7-9
                energy_level=6 + (i % 4),  # Varies between 6-9
                notes=f"Day {i+1} - Feeling good overall",
                recorded_at=entry_date
            )
            
            # Mood entry for user2
            mood2 = MoodEntry(
                user_id=user2.id,
                mood_score=5 + (i % 4),  # Varies between 5-8
                energy_level=5 + (i % 3),  # Varies between 5-7
                notes=f"Day {i+1} - Work stress affecting mood",
                recorded_at=entry_date
            )
            
            mood_entries.extend([mood1, mood2])
        
        db.add_all(mood_entries)
        db.commit()
        
        # Create sample therapy program
        print("🧘 Creating sample therapy program...")
        program = TherapyProgram(
            name="Anxiety Management Basics",
            description="A 7-day program to learn basic anxiety management techniques",
            duration_days=7,
            target_condition="anxiety",
            is_active=True
        )
        
        db.add(program)
        db.commit()
        
        # Create sample organization
        print("🏢 Creating sample organization...")
        org = Organization(
            name="MindEase Demo Clinic",
            description="Demo mental health clinic for testing",
            is_active=True
        )
        
        db.add(org)
        db.commit()
        
        print("✅ Database seeding completed successfully!")
        print(f"   - Created {db.query(User).count()} users")
        print(f"   - Created {db.query(Role).count()} roles")
        print(f"   - Created {db.query(Permission).count()} permissions")
        print(f"   - Created {db.query(Profile).count()} profiles")
        print(f"   - Created {db.query(MoodEntry).count()} mood entries")
        print(f"   - Created {db.query(TherapyProgram).count()} therapy programs")
        print(f"   - Created {db.query(Organization).count()} organizations")
        
        print("\n🔑 Test Credentials:")
        print("   Admin: admin@mindease.com / admin123")
        print("   User 1: john@example.com / password123")
        print("   User 2: jane@example.com / password123")
        print("   Therapist: therapist@mindease.com / therapist123")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        create_dummy_data()
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)

