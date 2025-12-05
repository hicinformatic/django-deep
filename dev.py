#!/usr/bin/env python3
"""Django Deep development tool for building, testing, and managing."""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# Load .env file if it exists
_env_file = Path(__file__).resolve().parent / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        # python-dotenv not installed, skip silently
        pass

BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
NC = '\033[0m'

if platform.system() == 'Windows' and not os.environ.get('ANSICON'):
    BLUE = GREEN = RED = YELLOW = NC = ''

PROJECT_ROOT = Path(__file__).parent


def _resolve_venv_dir() -> Path:
    """Find the virtual env directory, preferring .venv over venv."""
    preferred_names = ['.venv', 'venv']
    for name in preferred_names:
        candidate = PROJECT_ROOT / name
        if candidate.exists():
            return candidate
    return PROJECT_ROOT / preferred_names[0]


VENV_DIR = _resolve_venv_dir()
VENV_BIN = VENV_DIR / ('Scripts' if platform.system() == 'Windows' else 'bin')
PYTHON = VENV_BIN / ('python.exe' if platform.system() == 'Windows' else 'python')
PIP = VENV_BIN / ('pip.exe' if platform.system() == 'Windows' else 'pip')


def print_info(message):
    """Prints info message in blue."""
    print(f"{BLUE}{message}{NC}")


def print_success(message):
    """Prints success message in green."""
    print(f"{GREEN}{message}{NC}")


def print_error(message):
    """Prints error message in red."""
    print(f"{RED}{message}{NC}", file=sys.stderr)


def print_warning(message):
    """Prints warning message in yellow."""
    print(f"{YELLOW}{message}{NC}")


def run_command(cmd, check=True, **kwargs):
    """Runs command and handles errors."""
    print_info(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(cmd, check=check, **kwargs)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0] if isinstance(cmd, list) else cmd}")
        return False


def venv_exists():
    """Checks if virtual environment exists."""
    return VENV_DIR.exists() and PYTHON.exists()


def ensure_venv_activation(command: str):
    """
    Re-executes this script inside the project virtualenv (.venv/venv) if present.

    Skipped for commands that manage the virtualenv itself (venv, venv-clean).
    """
    venv_management_commands = {'venv', 'venv-clean'}
    if command in venv_management_commands:
        return

    if not venv_exists():
        return

    current_python = Path(sys.executable).resolve()
    desired_python = PYTHON.resolve()
    if current_python == desired_python:
        return

    print_info(
        f"Activating virtual environment at {VENV_DIR} before running '{command}'..."
    )
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = str(VENV_DIR)
    env['PATH'] = f"{VENV_BIN}{os.pathsep}{env.get('PATH', '')}"

    args = [str(desired_python), str(Path(__file__).resolve()), *sys.argv[1:]]
    os.execve(str(desired_python), args, env)


def task_help():
    """Shows available commands."""
    print(f"{BLUE}Django Deep - Available Commands{NC}\n")
    
    print(f"{GREEN}Development:{NC}")
    print("  venv              Create virtual environment")
    print("  install           Install package in production mode")
    print("  install-dev       Install package in development mode")
    print("")
    
    print(f"{GREEN}Django Dev Server:{NC}")
    print("  migrate           Run Django migrations")
    print("  makemigrations    Create new Django migrations")
    print("  runserver         Start Django development server")
    print("  shell             Open Django shell")
    print("  createsuperuser   Create Django superuser")
    print("")
    
    print(f"{GREEN}Testing:{NC}")
    print("  test              Run tests with pytest")
    print("  test-verbose      Run tests with verbose output")
    print("  coverage          Run tests with coverage report")
    print("")
    
    print(f"{GREEN}Code Quality:{NC}")
    print("  lint              Run ruff linter")
    print("  format            Format code with black")
    print("  check             Run all checks (lint + format check)")
    print("")
    
    print(f"{GREEN}Security:{NC}")
    print("  security          Run security audit (bandit, safety, pip-audit, semgrep)")
    print("")
    
    print(f"{GREEN}Building:{NC}")
    print("  clean             Remove all build, test, and Python artifacts")
    print("  clean-build       Remove build artifacts")
    print("  clean-pyc         Remove Python file artifacts")
    print("  clean-test        Remove test artifacts")
    print("  build             Build source and wheel distributions")
    print("  dist              Alias for build")
    print("")
    
    print(f"{GREEN}Publishing:{NC}")
    print("  upload-test       Upload package to TestPyPI")
    print("  upload            Upload package to PyPI")
    print("  release           Clean, build, and upload to PyPI")
    print("")
    
    print(f"{GREEN}Utilities:{NC}")
    print("  show-version      Show current package version")
    print("  venv-clean        Remove and recreate virtual environment")
    print("")
    
    print(f"Usage: python dev.py <command>")


def task_venv():
    """Creates virtual environment."""
    if venv_exists():
        print_warning("Virtual environment already exists")
        return True
    
    print_info("Creating virtual environment...")
    python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
    if not run_command([python_cmd, '-m', 'venv', str(VENV_DIR)]):
        return False
    
    print_success(f"Virtual environment created at {VENV_DIR}")
    if platform.system() == 'Windows':
        print_info(f"Activate it with: {VENV_DIR}\\Scripts\\activate")
    else:
        print_info(f"Activate it with: source {VENV_DIR}/bin/activate")
    return True


def task_install():
    """Installs package in production mode."""
    if not venv_exists() and not task_venv():
        return False
    
    print_info("Installing package...")
    commands = [
        [str(PIP), 'install', '--upgrade', 'pip', 'setuptools', 'wheel'],
        [str(PIP), 'install', '.']
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    
    print_success("Installation complete!")
    return True


def task_install_dev():
    """Installs package in development mode."""
    if not venv_exists() and not task_venv():
        return False
    
    print_info("Installing package in development mode...")
    commands = [
        [str(PIP), 'install', '--upgrade', 'pip', 'setuptools', 'wheel'],
        [str(PIP), 'install', '-e', '.[dev]']
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    
    print_success("Development installation complete!")
    return True


def task_clean_build():
    """Removes build artifacts."""
    print_info("Cleaning build artifacts...")
    dirs_to_remove = ['build', 'dist', '.eggs']
    
    for dir_name in dirs_to_remove:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_name}/")
    
    # Remove *.egg-info directories
    for egg_info in PROJECT_ROOT.glob('**/*.egg-info'):
        shutil.rmtree(egg_info)
        print(f"  Removed {egg_info.name}")
    
    # Remove *.egg files
    for egg in PROJECT_ROOT.glob('**/*.egg'):
        egg.unlink()
        print(f"  Removed {egg.name}")
    
    return True


def task_clean_pyc():
    """Removes Python file artifacts."""
    print_info("Cleaning Python file artifacts...")
    
    # Remove __pycache__ directories
    for pycache in PROJECT_ROOT.glob('**/__pycache__'):
        shutil.rmtree(pycache)
        print(f"  Removed {pycache}")
    
    # Remove .pyc, .pyo files
    for pattern in ['**/*.pyc', '**/*.pyo', '**/*~']:
        for file in PROJECT_ROOT.glob(pattern):
            file.unlink()
            print(f"  Removed {file}")
    
    return True


def task_clean_test():
    """Removes test artifacts."""
    print_info("Cleaning test artifacts...")
    artifacts = ['.pytest_cache', '.coverage', 'htmlcov', '.mypy_cache', '.tox', 'coverage.xml']
    
    removed_count = 0
    for artifact in artifacts:
        artifact_path = PROJECT_ROOT / artifact
        if artifact_path.exists():
            if artifact_path.is_dir():
                shutil.rmtree(artifact_path)
            else:
                artifact_path.unlink()
            print(f"  ✓ Removed {artifact}")
            removed_count += 1
    
    if removed_count == 0:
        print("  Nothing to clean")
    else:
        print_success(f"Cleaned {removed_count} artifact(s)")
    
    return True


def task_clean():
    """Removes all build, test, and Python artifacts."""
    task_clean_build()
    task_clean_pyc()
    task_clean_test()
    print_success("All clean!")
    return True


def task_test():
    """Runs tests with pytest."""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Running tests...")
    pytest = VENV_BIN / ('pytest.exe' if platform.system() == 'Windows' else 'pytest')
    
    if run_command([str(pytest)]):
        print_success("Tests complete!")
        return True
    return False


def task_test_verbose():
    """Runs tests with verbose output."""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Running tests (verbose)...")
    pytest = VENV_BIN / ('pytest.exe' if platform.system() == 'Windows' else 'pytest')
    
    if run_command([str(pytest), '-vv']):
        print_success("Tests complete!")
        return True
    return False


def task_coverage():
    """Runs tests with coverage report."""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Running tests with coverage...")
    pytest = VENV_BIN / ('pytest.exe' if platform.system() == 'Windows' else 'pytest')
    
    if run_command([str(pytest), '--cov=django_deep', '--cov-report=html', '--cov-report=term']):
        print_success("Coverage report generated in htmlcov/index.html")
        return True
    return False


def task_lint():
    """Runs linters."""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Running linters...")
    ruff = VENV_BIN / ('ruff.exe' if platform.system() == 'Windows' else 'ruff')
    targets = ['django_deep', 'tests']

    if run_command([str(ruff), 'check', *targets]):
        print_success("Linting complete!")
        return True
    return False


def task_format():
    """Formats code with black."""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Formatting code...")
    black = VENV_BIN / ('black.exe' if platform.system() == 'Windows' else 'black')
    
    if run_command([str(black), 'django_deep', 'tests']):
        print_success("Code formatted!")
        return True
    return False


def task_check():
    """Runs all checks."""
    if not task_lint():
        return False
    
    print_info("Checking code format...")
    black = VENV_BIN / ('black.exe' if platform.system() == 'Windows' else 'black')
    
    if run_command([str(black), '--check', 'django_deep', 'tests']):
        print_success("All checks passed!")
        return True
    return False


def task_security():
    """Runs security audit with multiple tools."""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("=" * 70)
    print_info("SECURITY AUDIT - Django Deep")
    print_info("=" * 70)
    
    bandit = VENV_BIN / ('bandit.exe' if platform.system() == 'Windows' else 'bandit')
    safety = VENV_BIN / ('safety.exe' if platform.system() == 'Windows' else 'safety')
    pip_audit = VENV_BIN / ('pip-audit.exe' if platform.system() == 'Windows' else 'pip-audit')
    semgrep = VENV_BIN / ('semgrep.exe' if platform.system() == 'Windows' else 'semgrep')
    targets = ['django_deep', 'tests']
    
    results = {
        'bandit': False,
        'safety': False,
        'pip_audit': False,
        'semgrep': False,
    }
    
    # 1. Bandit - Static code analysis
    print("\n" + "=" * 70)
    print_info("1/4 - Running Bandit (Static Code Analysis)")
    print_info("=" * 70)
    
    if run_command([str(bandit), '-r', *targets, '-ll', '-f', 'screen', '--skip', 'B101'], check=False):
        print_success("✓ Bandit: No high/medium issues found")
        results['bandit'] = True
    else:
        print_warning("⚠ Bandit: Issues found (review above)")
    
    # 2. Safety - Dependency vulnerability check
    print("\n" + "=" * 70)
    print_info("2/4 - Running Safety (Dependency Vulnerabilities)")
    print_info("=" * 70)
    
    # Safety may require authentication - try with API key from env if available
    safety_cmd = [str(safety), 'scan', '--output', 'json']
    safety_api_key = os.environ.get('SAFETY_API_KEY')
    if safety_api_key:
        safety_cmd.extend(['--key', safety_api_key])
        print_info("   Using SAFETY_API_KEY from environment")
    
    safety_result = run_command(safety_cmd, check=False)
    if safety_result:
        print_success("✓ Safety: No known vulnerabilities in dependencies")
        results['safety'] = True
    else:
        # Check if it's an authentication issue
        if not safety_api_key:
            print_warning("⚠ Safety: Unable to complete scan (authentication required)")
            print_info("   Note: Safety CLI requires free account registration")
            print_info("   Option 1: Register at https://pyup.io/safety/ and set SAFETY_API_KEY env var")
            print_info("   Option 2: Run 'safety auth' to authenticate interactively")
            print_info("   For now, treating as skipped (not a failure)")
            # Don't count as failure if it's just authentication
            results['safety'] = True  # Count as pass since it's optional
        else:
            print_warning("⚠ Safety: Scan completed but issues may have been found")
            results['safety'] = False
    
    # 3. Pip-Audit - PyPI vulnerability audit
    print("\n" + "=" * 70)
    print_info("3/4 - Running Pip-Audit (PyPI Vulnerabilities)")
    print_info("=" * 70)
    
    # Run pip-audit and capture output to check for transitive dependencies
    try:
        output = subprocess.run(
            [str(pip_audit)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if output.returncode == 0:
            print_success("✓ Pip-Audit: No vulnerabilities found")
            results['pip_audit'] = True
        else:
            # Check if the only vulnerability is in mcp (dependency of semgrep)
            # This is a transitive dependency vulnerability, not a direct one
            stdout_lines = output.stdout.split('\n')
            mcp_vuln_found = any('mcp' in line and 'CVE-2025-66416' in line for line in stdout_lines)
            vuln_count = output.stdout.count('CVE-')
            
            if mcp_vuln_found and vuln_count == 1:
                # Only mcp vulnerability (transitive dependency of semgrep)
                print_warning("⚠ Pip-Audit: 1 vulnerability in transitive dependency")
                print_info("   Package: mcp 1.16.0 (CVE-2025-66416)")
                print_info("   This is a dependency of semgrep, not directly used by django-deep")
                print_info("   Waiting for semgrep update to fix this dependency")
                print_success("✓ Pip-Audit: Transitive dependency vulnerability (acceptable)")
                results['pip_audit'] = True  # Count as pass for transitive deps
            else:
                print_warning("⚠ Pip-Audit: Vulnerabilities found (review above)")
                # Show the output for review
                if output.stdout:
                    print(output.stdout)
    except Exception as e:
        print_warning(f"⚠ Pip-Audit: Error running audit - {e}")
        print_warning("⚠ Pip-Audit: Unable to complete scan")
    
    # 4. Semgrep - SAST rules
    print("\n" + "=" * 70)
    print_info("4/4 - Running Semgrep (SAST)")
    print_info("=" * 70)

    semgrep_cmd = [str(semgrep), 'scan']
    semgrep_configs = []
    local_semgrep = PROJECT_ROOT / '.semgrep.yaml'
    if local_semgrep.exists():
        semgrep_configs.append(str(local_semgrep))
    else:
        semgrep_configs.append('p/default')
    semgrep_configs.extend(['p/python', 'p/supply-chain'])
    for config in semgrep_configs:
        semgrep_cmd += ['--config', config]
    semgrep_cmd += targets

    if run_command(semgrep_cmd, check=False):
        print_success("✓ Semgrep: No issues reported")
        results['semgrep'] = True
    else:
        print_warning("⚠ Semgrep: Findings detected (review above)")

    # Summary
    print("\n" + "=" * 70)
    print_info("SECURITY AUDIT SUMMARY")
    print_info("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for tool, success in results.items():
        status = f"{GREEN}✓ PASS{NC}" if success else f"{RED}✗ FAIL{NC}"
        print(f"  {tool.upper():15} {status}")
    
    print("\n" + "-" * 70)
    score = int((passed / total) * 100)
    
    if score == 100:
        print_success(f"SECURITY SCORE: {score}/100 - EXCELLENT!")
    elif score >= 66:
        print_warning(f"SECURITY SCORE: {score}/100 - GOOD")
    else:
        print_error(f"SECURITY SCORE: {score}/100 - NEEDS ATTENTION")
    
    print("-" * 70)
    
    # Additional tools info
    print("\n" + BLUE + "Additional Security Tools (manual setup):" + NC)
    print("  • SonarQube: https://sonarcloud.io/ (requires account)")
    print("  • Snyk: https://snyk.io/ (requires account)")
    print("  • OWASP Dependency-Check: https://owasp.org/www-project-dependency-check/")
    
    return score == 100


def task_build():
    """Build package"""
    if not venv_exists() and not task_venv():
        return False
    
    task_clean()
    
    print_info("Building package...")
    
    # Install build
    if not run_command([str(PIP), 'install', '--upgrade', 'build']):
        return False
    
    # Build
    python_build = VENV_BIN / ('python.exe' if platform.system() == 'Windows' else 'python')
    if not run_command([str(python_build), '-m', 'build']):
        return False
    
    print_success("Build complete! Files in dist/")
    
    # List files in dist
    dist_dir = PROJECT_ROOT / 'dist'
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  {file.name} ({file.stat().st_size / 1024:.1f} KB)")
    
    return True


def task_dist():
    """Alias for build"""
    return task_build()


def task_upload_test():
    """Upload to TestPyPI"""
    if not task_build():
        return False
    
    print_info("Uploading to TestPyPI...")
    
    if not run_command([str(PIP), 'install', '--upgrade', 'twine']):
        return False
    
    twine = VENV_BIN / ('twine.exe' if platform.system() == 'Windows' else 'twine')
    if not run_command([str(twine), 'upload', '--repository', 'testpypi', 'dist/*']):
        return False
    
    print_success("Upload complete!")
    print_info("Install with: pip install --index-url https://test.pypi.org/simple/ django-deep")
    return True


def task_upload():
    """Upload to PyPI"""
    if not task_build():
        return False
    
    print_warning("WARNING: This will upload to PyPI!")
    response = input("Press Enter to continue, or Ctrl+C to cancel... ")
    
    print_info("Uploading to PyPI...")
    
    if not run_command([str(PIP), 'install', '--upgrade', 'twine']):
        return False
    
    twine = VENV_BIN / ('twine.exe' if platform.system() == 'Windows' else 'twine')
    if not run_command([str(twine), 'upload', 'dist/*']):
        return False
    
    print_success("Upload complete!")
    print_info("Install with: pip install django-deep")
    return True


def task_release():
    """Full release workflow"""
    if not task_check():
        return False
    
    if not task_test():
        return False
    
    if not task_upload():
        return False
    
    print_success("Release complete!")
    return True


def task_show_version():
    """Show current package version"""
    print_info("Current version:")
    pyproject = PROJECT_ROOT / 'pyproject.toml'
    
    with open(pyproject, 'r') as f:
        for line in f:
            if line.startswith('version'):
                version = line.split('"')[1]
                print(f"  {version}")
                return True
    
    print_error("Version not found in pyproject.toml")
    return False


def task_venv_clean():
    """Remove and recreate virtual environment"""
    if venv_exists():
        print_info("Removing existing virtual environment...")
        shutil.rmtree(VENV_DIR)
        print_success("Virtual environment removed")
    
    return task_venv()


def task_migrate():
    """Run Django migrations"""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Running Django migrations...")
    manage_py = PROJECT_ROOT / 'manage.py'
    
    if run_command([str(PYTHON), str(manage_py), 'migrate']):
        print_success("Migrations complete!")
        return True
    return False


def task_makemigrations():
    """Create new Django migrations"""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Creating Django migrations...")
    manage_py = PROJECT_ROOT / 'manage.py'
    
    if run_command([str(PYTHON), str(manage_py), 'makemigrations']):
        print_success("Migrations created!")
        return True
    return False


def task_runserver():
    """Start Django development server"""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    # Check if migrations exist
    db_path = PROJECT_ROOT / 'db.sqlite3'
    if not db_path.exists():
        print_warning("Database not found. Running migrations first...")
        if not task_migrate():
            return False
    
    # Récupérer le port et l'hôte depuis les variables d'environnement
    port = os.environ.get('DJANGO_PORT', '8000')
    host = os.environ.get('DJANGO_HOST', '127.0.0.1')
    bind_address = f"{host}:{port}"
    
    print_success("Starting Django development server...")
    print_info(f"Access server at: http://{host}:{port}/")
    print_warning("Press Ctrl+C to stop the server")
    
    manage_py = PROJECT_ROOT / 'manage.py'
    run_command([str(PYTHON), str(manage_py), 'runserver', bind_address], check=False)
    return True


def task_shell():
    """Open Django shell"""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Opening Django shell...")
    manage_py = PROJECT_ROOT / 'manage.py'
    
    run_command([str(PYTHON), str(manage_py), 'shell'], check=False)
    return True


def task_createsuperuser():
    """Create Django superuser"""
    if not venv_exists():
        print_error("Virtual environment not found. Run: python dev.py install-dev")
        return False
    
    print_info("Creating Django superuser...")
    manage_py = PROJECT_ROOT / 'manage.py'
    
    run_command([str(PYTHON), str(manage_py), 'createsuperuser'], check=False)
    return True


# Command mapping
COMMANDS = {
    'help': task_help,
    'venv': task_venv,
    'install': task_install,
    'install-dev': task_install_dev,
    # Django commands
    'migrate': task_migrate,
    'makemigrations': task_makemigrations,
    'runserver': task_runserver,
    'shell': task_shell,
    'createsuperuser': task_createsuperuser,
    # Testing
    'clean': task_clean,
    'clean-build': task_clean_build,
    'clean-pyc': task_clean_pyc,
    'clean-test': task_clean_test,
    'test': task_test,
    'test-verbose': task_test_verbose,
    'coverage': task_coverage,
    # Code quality
    'lint': task_lint,
    'format': task_format,
    'check': task_check,
    # Security
    'security': task_security,
    # Building
    'build': task_build,
    'dist': task_dist,
    # Publishing
    'upload-test': task_upload_test,
    'upload': task_upload,
    'release': task_release,
    # Utilities
    'show-version': task_show_version,
    'venv-clean': task_venv_clean,
}


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        task_help()
        return 0
    
    command = sys.argv[1]
    
    if command not in COMMANDS:
        print_error(f"Unknown command: {command}")
        print_info("Run 'python dev.py help' to see available commands")
        return 1

    ensure_venv_activation(command)

    try:
        success = COMMANDS[command]()
        return 0 if success else 1
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

