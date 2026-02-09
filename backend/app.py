from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from db import connect_databases
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production-min-32-chars')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production-min-32-chars-long')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@app.com')

# Initialize extensions
CORS(app, resources={r"/api/*": {
    "origins": os.getenv('CORS_ORIGINS', '*').split(','),
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})
api = Api(app)
jwt = JWTManager(app)
mail = Mail(app)

# MongoDB Connection
try:
    connect_databases()
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")

# Import routes
from routes.mensajes_privados import mensajes_privados_bp
from routes.mensajes import mensajes_bp
from routes.seguidores import seguidores_bp
from routes.tendencias import tendencias_bp
from routes.testing import testing_bp

# Register blueprints
app.register_blueprint(mensajes_privados_bp, url_prefix='/api')
app.register_blueprint(mensajes_bp, url_prefix='/api')
app.register_blueprint(seguidores_bp, url_prefix='/api')
app.register_blueprint(tendencias_bp, url_prefix='/api')
app.register_blueprint(testing_bp, url_prefix='/api')  # Testing routes

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Backend API',
        'version': '1.0.0'
    }), 200

# Server-Sent Events example endpoint
@app.route('/api/stream', methods=['GET'])
def stream():
    def generate():
        import time
        for i in range(10):
            yield f"data: {{'message': 'Event {i}', 'timestamp': {time.time()}}}\n\n"
            time.sleep(1)
    
    return app.response_class(generate(), mimetype='text/event-stream')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
