"""Verify API routes, router registration, and frontend routes."""
import re
import os

base = "/sessions/beautiful-nice-hamilton/mnt/Kids-Star"

print("=" * 50)
print("1. BACKEND API ROUTES")
print("=" * 50)

# Check auth.py endpoints
auth_file = os.path.join(base, "backend/app/api/v1/auth.py")
with open(auth_file) as f:
    auth_content = f.read()

endpoints = re.findall(r'@router\.(get|post|put|delete|patch)\(\s*"([^"]+)"', auth_content)
for method, path in endpoints:
    print(f"  {method.upper():6s} /api/v1/auth{path}")

print(f"\n  Total auth endpoints: {len(endpoints)}")

# Check main.py router registration
main_file = os.path.join(base, "backend/main.py")
with open(main_file) as f:
    main_content = f.read()

routers = re.findall(r'app\.include_router\((\w+)_router', main_content)
print(f"\n  Registered routers: {routers}")

print()
print("=" * 50)
print("2. FRONTEND ROUTES")
print("=" * 50)

router_file = os.path.join(base, "frontend/src/router/index.ts")
with open(router_file) as f:
    router_content = f.read()

routes = re.findall(r"path:\s*['\"]([^'\"]+)['\"]", router_content)
for r in routes:
    print(f"  {r}")
print(f"\n  Total frontend routes: {len(routes)}")

print()
print("=" * 50)
print("3. DEPS INJECTION CHAIN")
print("=" * 50)

deps_file = os.path.join(base, "backend/app/api/deps.py")
with open(deps_file) as f:
    deps_content = f.read()

functions = re.findall(r'async def (\w+)\(', deps_content)
for fn in functions:
    print(f"  {fn}()")
    # Check what it depends on
    deps = re.findall(r'Depends\((\w+)\)', deps_content)
print(f"\n  Dependency chain: {' -> '.join(deps[:6])}...")

print()
print("=" * 50)
print("4. DOCKER SERVICES")
print("=" * 50)

compose_file = os.path.join(base, "docker-compose.yml")
with open(compose_file) as f:
    compose = f.read()

services = re.findall(r'^\s{2}(\w+):', compose, re.MULTILINE)
for s in services:
    has_build = 'build:' in compose.split(s)[1].split('\n\n')[0] if s in compose else False
    has_image = 'image:' in compose.split(s)[1].split('\n\n')[0] if s in compose else False
    tag = "📦 build" if has_build else "🐳 image" if has_image else "⚙️  config"
    print(f"  {s:20s} {tag}")
print(f"\n  Total services: {len(services)}")
