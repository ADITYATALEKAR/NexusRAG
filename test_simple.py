#!/usr/bin/env python
import os
import sys

# Set env
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_ziqVbc5hrEH0@ep-spring-mode-a1ri1vbg-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
os.environ['OPENAI_API_KEY'] = 'AIzaSyDY-tCFvmB3P6Ne72DLC6CRRVELPZNGRaw'

print("=" * 80)
print("SIMPLE LOCAL TEST")
print("=" * 80)

print("\n[TEST 1] Database Connection")
try:
    import psycopg
    conn = psycopg.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    conn.close()
    print("PASS - Database connected successfully")
except Exception as e:
    print(f"FAIL - {e}")
    sys.exit(1)

print("\n[TEST 2] FastAPI Import")
try:
    from fastapi import FastAPI
    print("PASS - FastAPI imported")
except Exception as e:
    print(f"FAIL - {e}")
    sys.exit(1)

print("\n[TEST 3] App Modules")
try:
    sys.path.insert(0, '.')
    from apps.api.middleware.cors import normalize_origins
    from apps.api.routes.health import router as health_router
    print("PASS - Core modules imported")
except Exception as e:
    print(f"FAIL - {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("ALL TESTS PASSED - System ready for full integration test")
print("=" * 80)
