"""Verify models and migration tables match."""
import re
import os

base = "/sessions/beautiful-nice-hamilton/mnt/Kids-Star/backend"

# Count model tables
with open(os.path.join(base, "app/models/models.py")) as f:
    content = f.read()
model_tables = set(re.findall(r"__tablename__\s*=\s*['\"]([^'\"]+)['\"]", content))

# Count migration tables
with open(os.path.join(base, "alembic/versions/0001_initial.py")) as f:
    mig = f.read()
mig_create = set(re.findall(r'create_table\(\s*"([a-z_]+)"', mig))

print("=== Models ===")
for t in sorted(model_tables):
    print(f"  {t}")
print(f"Count: {len(model_tables)}")

print()
print("=== Migration ===")
for t in sorted(mig_create):
    status = "OK" if t in model_tables else "EXTRA"
    print(f"  [{status}] {t}")
print(f"Count: {len(mig_create)}")

missing = model_tables - mig_create
extra = mig_create - model_tables
if missing:
    print(f"\n*** MISSING from migration: {missing}")
if extra:
    print(f"\n*** EXTRA in migration (not in models): {extra}")
if not missing and not extra:
    print(f"\n*** PERFECT MATCH: All {len(model_tables)} model tables covered by migration")

# Also verify downgrade drops everything
downgrade_tables = set(re.findall(r'drop_table\(\s*"([a-z_]+)"', mig))
print(f"\n=== Downgrade drop count: {len(downgrade_tables)} ===")
not_dropped = mig_create - downgrade_tables
if not_dropped:
    print(f"*** NOT DROPPED in downgrade: {not_dropped}")
