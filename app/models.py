from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DiagnosticLog(db.Model):
    __tablename__ = 'diagnostic_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Epidemiological & Diagnostic Analytics
    predicted_condition = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    task_duration_ms = db.Column(db.Integer, nullable=True)
    outcome = db.Column(db.String(50), nullable=True) # e.g., 'success', 'error'
    
    # Facility & Device Metadata (Optional)
    facility_name = db.Column(db.String(255), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    device_type = db.Column(db.String(255), nullable=True)
    
    # User Feedback
    helpful_rating = db.Column(db.Integer, nullable=True) # 1 to 5 stars
    clinical_override = db.Column(db.Text, nullable=True)
