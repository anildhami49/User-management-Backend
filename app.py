# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv
from functools import wraps
import logging

# Load environment
load_dotenv()

# App setup
app = Flask(__name__)

# CORS configuration - Allow all Azure websites and localhost
CORS(app, 
     origins=[
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "https://usermanagementservices-frontend-atbzdze6fubebyb4.canadacentral-01.azurewebsites.net"
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True,
     expose_headers=["Content-Type", "Authorization"])

logging.basicConfig(level=logging.DEBUG)

# Config from env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'user_management_db')

# Validate critical environment variables
if not MONGO_URI:
    logging.error("CRITICAL: MONGO_URI environment variable is not set!")
    MONGO_URI = 'mongodb://localhost:27017/'  # Fallback for local testing

logging.info("Starting application...")
logging.info(f"Using database: {MONGO_DB_NAME}")
logging.info(f"MONGO_URI is set: {bool(MONGO_URI)}")

# MongoDB Connection
try:
    # Use TLS for Cosmos DB - increase timeout to 30 seconds
    logging.info(f"Attempting to connect to MongoDB...")
    client = MongoClient(
        MONGO_URI, 
        tls=True, 
        tlsAllowInvalidCertificates=False,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000
    )
    # Test connection
    client.server_info()
    logging.info("✅ Successfully connected to MongoDB")
    
    # Prefer explicit DB chosen via env to avoid writing to unexpected DB
    db = client[MONGO_DB_NAME]
    users_collection = db['users']
    profiles_collection = db['profiles']
    logging.info(f"✅ Using database: {MONGO_DB_NAME}")
    logging.info(f"✅ Collections initialized: users, profiles")
except Exception as e:
    logging.error(f"❌ Error connecting to MongoDB: {type(e).__name__}")
    logging.error(f"❌ Error details: {str(e)}")
    logging.exception("Full traceback:")
    # Don't crash - create dummy collections for startup
    db = None
    users_collection = None
    profiles_collection = None

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = users_collection.find_one({'_id': ObjectId(data['user_id'])})

            if not current_user:
                return jsonify({'message': 'User not found!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception as e:
            logging.exception("Token verification error: %s", e)
            return jsonify({'message': f'Token verification failed: {str(e)}'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json() or {}

        # Validate required fields
        if not data.get('email') or not data.get('password') or not data.get('username'):
            return jsonify({'message': 'Email, username, and password are required!'}), 400

        # Check if user already exists
        if users_collection.find_one({'email': data['email']}):
            return jsonify({'message': 'Email already registered!'}), 409

        if users_collection.find_one({'username': data['username']}):
            return jsonify({'message': 'Username already taken!'}), 409

        # Hash password - store as UTF-8 string to avoid Binary type mismatches
        hashed_bytes = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed_bytes.decode('utf-8')

        # Create user document
        user = {
            'username': data['username'],
            'email': data['email'],
            'password': hashed_str,  # store string
            'created_at': datetime.datetime.utcnow()
        }

        result = users_collection.insert_one(user)
        logging.debug("Inserted user id: %s", str(result.inserted_id))

        return jsonify({
            'message': 'User registered successfully!',
            'user_id': str(result.inserted_id)
        }), 201

    except Exception as e:
        logging.exception("Error during signup: %s", e)
        return jsonify({'message': f'Error during signup: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}

        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required!'}), 400

        # Find user
        user = users_collection.find_one({'email': data['email']})
        logging.debug("Login attempt for email=%s found_user=%s", data['email'], bool(user))

        if not user:
            return jsonify({'message': 'Invalid email or password!'}), 401

        # Stored hash is string; convert to bytes for bcrypt
        stored_hash = user.get('password')
        if isinstance(stored_hash, str):
            stored_hash_bytes = stored_hash.encode('utf-8')
        else:
            # If stored as Binary/bytes already
            stored_hash_bytes = stored_hash

        # Verify password
        if bcrypt.checkpw(data['password'].encode('utf-8'), stored_hash_bytes):
            # Generate token
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'message': 'Login successful!',
                'token': token,
                'username': user['username']
            }), 200
        else:
            logging.debug("Password mismatch for email=%s", data['email'])
            return jsonify({'message': 'Invalid email or password!'}), 401

    except Exception as e:
        logging.exception("Error during login: %s", e)
        return jsonify({'message': f'Error during login: {str(e)}'}), 500

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        profile = profiles_collection.find_one({'user_id': str(current_user['_id'])})

        if profile:
            profile['_id'] = str(profile['_id'])
            return jsonify({
                'profile': profile,
                'username': current_user['username'],
                'email': current_user['email']
            }), 200
        else:
            return jsonify({
                'message': 'No profile found',
                'username': current_user['username'],
                'email': current_user['email']
            }), 200

    except Exception as e:
        logging.exception("Error fetching profile: %s", e)
        return jsonify({'message': f'Error fetching profile: {str(e)}'}), 500

@app.route('/api/profile', methods=['POST'])
@token_required
def save_profile(current_user):
    try:
        data = request.get_json() or {}

        profile_data = {
            'user_id': str(current_user['_id']),
            'full_name': data.get('full_name', ''),
            'phone': data.get('phone', ''),
            'date_of_birth': data.get('date_of_birth', ''),
            'address': data.get('address', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'zip_code': data.get('zip_code', ''),
            'country': data.get('country', ''),
            'bio': data.get('bio', ''),
            'updated_at': datetime.datetime.utcnow()
        }

        # Update or insert profile
        result = profiles_collection.update_one(
            {'user_id': str(current_user['_id'])},
            {'$set': profile_data},
            upsert=True
        )

        return jsonify({
            'message': 'Profile saved successfully!',
            'profile': profile_data
        }), 200

    except Exception as e:
        logging.exception("Error saving profile: %s", e)
        return jsonify({'message': f'Error saving profile: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    mongo_status = "connected" if db is not None else "disconnected"
    return jsonify({
        'status': 'healthy', 
        'message': 'Backend is running!',
        'mongodb': mongo_status,
        'database': MONGO_DB_NAME
    }), 200

# Root route for Azure health check
@app.route('/', methods=['GET'])
def root():
    mongo_status = "connected" if db is not None else "disconnected"
    return jsonify({
        'status': 'online',
        'message': 'User Management Backend API',
        'version': '1.0.0',
        'mongodb': mongo_status,
        'endpoints': ['/api/signup', '/api/login', '/api/profile', '/api/health']
    }), 200

if __name__ == '__main__':
    # Azure sets PORT environment variable
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

# For gunicorn - expose the app at module level
application = app
