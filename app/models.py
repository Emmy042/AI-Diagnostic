from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=convention))

class Region(db.Model):
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    facilities = db.relationship('Facility', backref='region', lazy=True)

class Facility(db.Model):
    __tablename__ = 'facilities'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    logs = db.relationship('DiagnosticLog', backref='facility', lazy=True)

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
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), nullable=True)
    device_type = db.Column(db.String(255), nullable=True)
    
    # User Feedback
    helpful_rating = db.Column(db.Integer, nullable=True) # 1 to 5 stars
    clinical_override = db.Column(db.Text, nullable=True)
