import os
import sys

os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_ziqVbc5hrEH0@ep-spring-mode-a1ri1vbg-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
os.environ['OPENAI_API_KEY'] = 'AIzaSyDY-tCFvmB3P6Ne72DLC6CRRVELPZNGRaw'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDY-tCFvmB3P6Ne72DLC6CRRVELPZNGRaw'
os.environ['RAG__SECURITY__CORS_ORIGINS'] = '*'
os.environ['RAG__SECURITY__API_KEY_REQUIRED'] = 'false'

sys.path.insert(0, '.')

import uvicorn
from apps.api.main import app

print("Starting server on http://localhost:8000")
uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
