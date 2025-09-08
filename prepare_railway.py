"""
Railway Deployment Preparation Script
This script helps you prepare your project for Railway deployment.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_file_exists(filename):
    """Check if a required file exists."""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    return exists

def check_git_status():
    """Check git repository status."""
    try:
        # Check if we're in a git repo
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository detected")
            
            # Check for uncommitted changes
            if "nothing to commit" in result.stdout:
                print("✅ No uncommitted changes")
            else:
                print("⚠️  You have uncommitted changes")
                print("   Run: git add . && git commit -m 'Prepare for Railway deployment'")
            
            # Check remote
            remote_result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
            if remote_result.returncode == 0 and remote_result.stdout:
                print("✅ Git remote configured")
            else:
                print("❌ No git remote found")
                print("   Add remote: git remote add origin https://github.com/yourusername/yourrepo.git")
            
            return True
        else:
            print("❌ Not a git repository")
            print("   Initialize: git init && git add . && git commit -m 'Initial commit'")
            return False
    except FileNotFoundError:
        print("❌ Git not installed")
        return False

def check_requirements():
    """Check if all required dependencies are in requirements.txt."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'requests'
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements_content = f.read().lower()
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements_content:
                missing_packages.append(package)
        
        if not missing_packages:
            print("✅ All required packages in requirements.txt")
            return True
        else:
            print(f"❌ Missing packages in requirements.txt: {missing_packages}")
            return False
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def validate_dataset():
    """Validate the portfolio dataset."""
    try:
        with open('portfolio_dataset.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversations = data.get('conversations', [])
        if conversations:
            print(f"✅ Dataset loaded with {len(conversations)} conversations")
            return True
        else:
            print("❌ No conversations found in dataset")
            return False
            
    except FileNotFoundError:
        print("❌ portfolio_dataset.json not found")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in portfolio_dataset.json")
        return False
    except UnicodeDecodeError:
        print("❌ Character encoding issue in portfolio_dataset.json")
        print("   Try saving the file with UTF-8 encoding")
        return False

def generate_env_template():
    """Generate environment variables template for Railway."""
    env_template = """# Copy these environment variables to Railway dashboard

# Required
INTERSECT_API_KEY=your-super-secure-api-key-here-change-this
OLLAMA_URL=https://your-ollama-instance.railway.app
OLLAMA_MODEL=llama3.1

# Optional (with sensible defaults)
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW=60
ALLOWED_ORIGINS=https://tampertantrumlabs.com,https://www.tampertantrumlabs.com
LOG_LEVEL=info

# Railway sets these automatically
PORT=8000
RAILWAY_ENVIRONMENT=production
"""
    
    with open('railway_env_vars.txt', 'w') as f:
        f.write(env_template)
    
    print("✅ Created railway_env_vars.txt with environment variables template")

def main():
    """Main deployment preparation function."""
    print("🚂 Railway Deployment Preparation")
    print("=" * 50)
    
    # Check required files
    print("\n📁 Checking required files:")
    required_files = [
        'web_api.py',
        'portfolio_dataset.json',
        'dataset_manager.py',
        'ollama_chatbot.py',
        'requirements.txt',
        'railway.toml'
    ]
    
    all_files_exist = True
    for file in required_files:
        if not check_file_exists(file):
            all_files_exist = False
    
    # Check git status
    print("\n🔧 Checking git repository:")
    git_ready = check_git_status()
    
    # Check requirements
    print("\n📦 Checking dependencies:")
    requirements_ok = check_requirements()
    
    # Validate dataset
    print("\n📊 Checking dataset:")
    dataset_ok = validate_dataset()
    
    # Generate environment template
    print("\n🔐 Environment variables:")
    generate_env_template()
    
    # Final status
    print("\n" + "=" * 50)
    print("🎯 Deployment Readiness Check:")
    
    if all_files_exist and git_ready and requirements_ok and dataset_ok:
        print("✅ Ready for Railway deployment!")
        print("\n🚀 Next steps:")
        print("1. Push your code to GitHub:")
        print("   git add . && git commit -m 'Prepare for Railway' && git push")
        print("2. Go to railway.app and create new project from GitHub")
        print("3. Set environment variables from railway_env_vars.txt")
        print("4. Deploy Ollama service or configure external Ollama URL")
        print("5. Test your deployed API")
        
    else:
        print("❌ Not ready for deployment. Fix the issues above first.")
    
    print(f"\n📖 See RAILWAY_DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    main()
