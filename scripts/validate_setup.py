#!/usr/bin/env python3
"""
Validation script for MindEase v3 setup
Validates all configurations and implementations
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")

def validate_file_exists(filepath, description):
    """Validate that a file exists"""
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} not found: {filepath}")
        return False

def validate_yaml_file(filepath):
    """Validate YAML syntax"""
    try:
        with open(filepath, 'r') as f:
            yaml.safe_load(f)
        print_success(f"Valid YAML: {filepath}")
        return True
    except Exception as e:
        print_error(f"Invalid YAML {filepath}: {e}")
        return False

def validate_json_file(filepath):
    """Validate JSON syntax"""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        print_success(f"Valid JSON: {filepath}")
        return True
    except Exception as e:
        print_error(f"Invalid JSON {filepath}: {e}")
        return False

def validate_sonar_config():
    """Validate SonarQube configuration"""
    print_info("Validating SonarQube configuration...")
    
    if not validate_file_exists('sonar-project.properties', 'SonarQube config'):
        return False
    
    with open('sonar-project.properties', 'r') as f:
        content = f.read()
    
    required_props = [
        'sonar.projectKey=',
        'sonar.projectName=',
        'sonar.sources=',
        'sonar.organization='
    ]
    
    all_valid = True
    for prop in required_props:
        if prop in content:
            line = [l for l in content.split('\n') if l.startswith(prop)][0]
            print_success(f"SonarQube property: {line}")
        else:
            print_error(f"Missing SonarQube property: {prop}")
            all_valid = False
    
    return all_valid

def validate_github_workflows():
    """Validate GitHub Actions workflows"""
    print_info("Validating GitHub Actions workflows...")
    
    workflows = [
        '.github/workflows/ci.yml',
        '.github/workflows/deploy.yml',
        '.github/workflows/security.yml',
        '.github/workflows/monitoring.yml'
    ]
    
    all_valid = True
    for workflow in workflows:
        if validate_file_exists(workflow, 'GitHub workflow'):
            if not validate_yaml_file(workflow):
                all_valid = False
        else:
            all_valid = False
    
    return all_valid

def validate_docker_config():
    """Validate Docker configuration"""
    print_info("Validating Docker configuration...")
    
    if not validate_file_exists('docker-compose.yml', 'Docker Compose'):
        return False
    
    if not validate_yaml_file('docker-compose.yml'):
        return False
    
    # Check for required services
    with open('docker-compose.yml', 'r') as f:
        compose_config = yaml.safe_load(f)
    
    required_services = [
        'postgres', 'redis', 'backend', 'frontend', 
        'nginx', 'sonarqube', 'prometheus', 'grafana'
    ]
    
    services = compose_config.get('services', {})
    all_valid = True
    
    for service in required_services:
        if service in services:
            print_success(f"Docker service configured: {service}")
        else:
            print_error(f"Missing Docker service: {service}")
            all_valid = False
    
    return all_valid

def validate_monitoring_config():
    """Validate monitoring configuration"""
    print_info("Validating monitoring configuration...")
    
    configs = [
        ('monitoring/prometheus.yml', 'Prometheus config'),
        ('monitoring/grafana/datasources/prometheus.yml', 'Grafana datasource'),
        ('monitoring/grafana/dashboards/dashboard.yml', 'Grafana dashboard'),
        ('.github/lighthouse/lighthouserc.json', 'Lighthouse config')
    ]
    
    all_valid = True
    for filepath, description in configs:
        if validate_file_exists(filepath, description):
            if filepath.endswith('.yml') or filepath.endswith('.yaml'):
                if not validate_yaml_file(filepath):
                    all_valid = False
            elif filepath.endswith('.json'):
                if not validate_json_file(filepath):
                    all_valid = False
        else:
            all_valid = False
    
    return all_valid

def validate_security_config():
    """Validate security configuration"""
    print_info("Validating security configuration...")
    
    security_files = [
        'backend/mindease-api/app/core/security_enhanced.py',
        'backend/mindease-api/app/core/gdpr_compliance.py',
        '.env.example'
    ]
    
    all_valid = True
    for filepath in security_files:
        if not validate_file_exists(filepath, f'Security file'):
            all_valid = False
    
    return all_valid

def validate_test_config():
    """Validate test configuration"""
    print_info("Validating test configuration...")
    
    test_configs = [
        ('backend/mindease-api/pytest.ini', 'Backend test config'),
        ('frontend/mindease-web/jest.config.js', 'Frontend test config'),
        ('frontend/mindease-web/jest.setup.js', 'Frontend test setup')
    ]
    
    all_valid = True
    for filepath, description in test_configs:
        if not validate_file_exists(filepath, description):
            all_valid = False
    
    return all_valid

def validate_project_structure():
    """Validate overall project structure"""
    print_info("Validating project structure...")
    
    required_dirs = [
        'backend/mindease-api',
        'frontend/mindease-web',
        'nginx',
        'monitoring',
        '.github/workflows',
        'scripts'
    ]
    
    all_valid = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            print_success(f"Directory exists: {directory}")
        else:
            print_error(f"Missing directory: {directory}")
            all_valid = False
    
    return all_valid

def main():
    """Main validation function"""
    print_info("🔍 Starting MindEase v3 Setup Validation")
    print("=" * 50)
    
    validations = [
        ("Project Structure", validate_project_structure),
        ("SonarQube Configuration", validate_sonar_config),
        ("GitHub Workflows", validate_github_workflows),
        ("Docker Configuration", validate_docker_config),
        ("Monitoring Configuration", validate_monitoring_config),
        ("Security Configuration", validate_security_config),
        ("Test Configuration", validate_test_config)
    ]
    
    results = {}
    
    for name, validator in validations:
        print(f"\n{Colors.BLUE}📋 {name}{Colors.END}")
        print("-" * 30)
        results[name] = validator()
    
    # Summary
    print(f"\n{Colors.BLUE}📊 VALIDATION SUMMARY{Colors.END}")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{total} validations passed")
    
    if passed == total:
        print_success("🎉 All validations passed! Setup is complete.")
        return 0
    else:
        print_error(f"❌ {total - passed} validation(s) failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

