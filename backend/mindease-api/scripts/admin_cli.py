#!/usr/bin/env python3
"""
Admin CLI Tools for MindEase API

Command-line interface for administrative operations.
"""

import asyncio
import click
import sys
import os
from typing import Optional

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import get_settings
from app.db.session import get_async_session
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.db.models.auth import User, Role
from app.db.models.organization import Organization

settings = get_settings()


@click.group()
def cli():
    """MindEase API Admin CLI Tools"""
    pass


@cli.command()
@click.option('--email', prompt=True, help='Admin email address')
@click.option('--password', prompt=True, hide_input=True, help='Admin password')
@click.option('--first-name', prompt=True, help='First name')
@click.option('--last-name', prompt=True, help='Last name')
@click.option('--org-name', default='MindEase', help='Organization name')
async def create_admin(email: str, password: str, first_name: str, last_name: str, org_name: str):
    """Create a new admin user."""
    try:
        async with get_async_session() as session:
            auth_service = AuthService(session)
            
            # Check if user already exists
            existing_user = await auth_service.get_user_by_email(email)
            if existing_user:
                click.echo(f"Error: User with email {email} already exists")
                return
            
            # Create organization if it doesn't exist
            org = await session.query(Organization).filter(Organization.name == org_name).first()
            if not org:
                org = Organization(
                    name=org_name,
                    domain=email.split('@')[1],
                    is_active=True
                )
                session.add(org)
                await session.flush()
            
            # Create admin user
            user_data = {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
                'is_admin': True,
                'organization_id': org.id
            }
            
            user = await auth_service.create_user(user_data)
            await session.commit()
            
            click.echo(f"Admin user created successfully:")
            click.echo(f"  Email: {user.email}")
            click.echo(f"  Name: {user.first_name} {user.last_name}")
            click.echo(f"  Organization: {org.name}")
            
    except Exception as e:
        click.echo(f"Error creating admin user: {str(e)}")


@cli.command()
@click.option('--email', prompt=True, help='User email address')
async def delete_user(email: str):
    """Delete a user by email."""
    try:
        async with get_async_session() as session:
            auth_service = AuthService(session)
            
            user = await auth_service.get_user_by_email(email)
            if not user:
                click.echo(f"Error: User with email {email} not found")
                return
            
            if click.confirm(f"Are you sure you want to delete user {email}?"):
                await session.delete(user)
                await session.commit()
                click.echo(f"User {email} deleted successfully")
            else:
                click.echo("Operation cancelled")
                
    except Exception as e:
        click.echo(f"Error deleting user: {str(e)}")


@cli.command()
async def list_users():
    """List all users."""
    try:
        async with get_async_session() as session:
            users = await session.query(User).all()
            
            click.echo(f"Total users: {len(users)}")
            click.echo("-" * 80)
            
            for user in users:
                status = "Active" if user.is_active else "Inactive"
                admin = "Admin" if user.is_admin else "User"
                click.echo(f"{user.email:<30} {user.first_name} {user.last_name:<20} {admin:<10} {status}")
                
    except Exception as e:
        click.echo(f"Error listing users: {str(e)}")


@cli.command()
async def system_health():
    """Check system health."""
    try:
        from app.core.monitoring import get_system_health
        
        health = await get_system_health()
        
        click.echo(f"Overall Status: {health['overall_status'].upper()}")
        click.echo(f"Timestamp: {health['timestamp']}")
        click.echo("-" * 50)
        
        for service, status in health['checks'].items():
            status_color = 'green' if status['status'] == 'healthy' else 'red'
            click.echo(f"{service:<20} {status['status']:<10} {status['response_time']:.3f}s")
            
            if status.get('error'):
                click.echo(f"  Error: {status['error']}")
                
    except Exception as e:
        click.echo(f"Error checking system health: {str(e)}")


@cli.command()
@click.option('--hours', default=24, help='Number of hours to include in metrics')
async def system_metrics(hours: int):
    """Get system metrics."""
    try:
        from app.core.monitoring import get_detailed_metrics
        
        metrics = await get_detailed_metrics(hours)
        
        click.echo(f"System Metrics (Last {hours} hours)")
        click.echo("-" * 50)
        
        current = metrics['current']
        click.echo(f"CPU Usage: {current['cpu_percent']:.1f}%")
        click.echo(f"Memory Usage: {current['memory_percent']:.1f}%")
        click.echo(f"Disk Usage: {current['disk_percent']:.1f}%")
        click.echo(f"Active Connections: {current['active_connections']}")
        click.echo(f"Avg Response Time: {current['response_time_avg']:.3f}s")
        click.echo(f"Error Rate: {current['error_rate']:.2f}%")
        
        if 'summary' in metrics and 'averages' in metrics['summary']:
            click.echo("\nAverages:")
            summary = metrics['summary']['averages']
            click.echo(f"  CPU: {summary['cpu_percent']:.1f}%")
            click.echo(f"  Memory: {summary['memory_percent']:.1f}%")
            click.echo(f"  Response Time: {summary['response_time_ms']:.1f}ms")
            click.echo(f"  Error Rate: {summary['error_rate_percent']:.2f}%")
            
    except Exception as e:
        click.echo(f"Error getting system metrics: {str(e)}")


@cli.command()
@click.option('--dataset-path', prompt=True, help='Path to dataset file')
@click.option('--dataset-name', prompt=True, help='Dataset name')
@click.option('--category', default='general', help='Dataset category')
async def upload_dataset(dataset_path: str, dataset_name: str, category: str):
    """Upload a dataset for processing."""
    try:
        if not os.path.exists(dataset_path):
            click.echo(f"Error: File {dataset_path} not found")
            return
        
        async with get_async_session() as session:
            admin_service = AdminService(session)
            
            with open(dataset_path, 'rb') as f:
                file_content = f.read()
            
            # Simulate file upload
            class MockFile:
                def __init__(self, content, filename):
                    self.content = content
                    self.filename = filename
                
                async def read(self):
                    return self.content
            
            mock_file = MockFile(file_content, os.path.basename(dataset_path))
            
            result = await admin_service.upload_dataset(
                file=mock_file,
                dataset_name=dataset_name,
                category=category,
                validate_before_load=True,
                organization_id=1  # Default organization
            )
            
            click.echo(f"Dataset uploaded successfully:")
            click.echo(f"  Name: {result['dataset_name']}")
            click.echo(f"  Documents processed: {result['documents_processed']}")
            click.echo(f"  Processing time: {result['processing_time']:.2f}s")
            
    except Exception as e:
        click.echo(f"Error uploading dataset: {str(e)}")


@cli.command()
async def cleanup_cache():
    """Clean up Redis cache."""
    try:
        from app.core.cache import get_redis_client
        
        redis_client = await get_redis_client()
        
        # Get cache statistics before cleanup
        info_before = await redis_client.info()
        keys_before = len(await redis_client.keys('*'))
        
        # Clean up expired keys
        await redis_client.flushdb()
        
        # Get statistics after cleanup
        info_after = await redis_client.info()
        
        click.echo("Cache cleanup completed:")
        click.echo(f"  Keys removed: {keys_before}")
        click.echo(f"  Memory freed: {info_before.get('used_memory', 0) - info_after.get('used_memory', 0)} bytes")
        
    except Exception as e:
        click.echo(f"Error cleaning up cache: {str(e)}")


@cli.command()
async def run_migrations():
    """Run database migrations."""
    try:
        import subprocess
        
        click.echo("Running database migrations...")
        
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        if result.returncode == 0:
            click.echo("Migrations completed successfully")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.echo(f"Migration failed: {result.stderr}")
            
    except Exception as e:
        click.echo(f"Error running migrations: {str(e)}")


@cli.command()
async def seed_database():
    """Seed database with initial data."""
    try:
        click.echo("Seeding database...")
        
        # Import and run the seed script
        from scripts.seed_db import main as seed_main
        await seed_main()
        
        click.echo("Database seeded successfully")
        
    except Exception as e:
        click.echo(f"Error seeding database: {str(e)}")


if __name__ == '__main__':
    # Run async commands
    import inspect
    
    def async_command(f):
        """Decorator to run async commands."""
        if inspect.iscoroutinefunction(f):
            def wrapper(*args, **kwargs):
                return asyncio.run(f(*args, **kwargs))
            return wrapper
        return f
    
    # Apply async wrapper to all commands
    for command in cli.commands.values():
        if hasattr(command, 'callback') and inspect.iscoroutinefunction(command.callback):
            command.callback = async_command(command.callback)
    
    cli()

