import os
from app.web import create_app
from app.models import db, Region, Facility

def seed():
    # Set to demo mode so we don't try to load the ML model just to seed the DB
    os.environ["DERMA_DEMO_MODE"] = "True"
    app = create_app()
    with app.app_context():
        # Add some sample Nigerian regions and facilities
        regions_data = [
            {
                "name": "Lagos", 
                "facilities": [
                    "General Hospital, Lagos", 
                    "Lagos University Teaching Hospital", 
                    "Ikeja Medical Centre"
                ]
            },
            {
                "name": "Abuja", 
                "facilities": [
                    "National Hospital Abuja", 
                    "Garki Hospital", 
                    "Asokoro District Hospital"
                ]
            },
            {
                "name": "Kano", 
                "facilities": [
                    "Aminu Kano Teaching Hospital", 
                    "Murtala Muhammed Specialist Hospital"
                ]
            },
            {
                "name": "Rivers", 
                "facilities": [
                    "University of Port Harcourt Teaching Hospital", 
                    "Braithwaite Memorial Specialist Hospital"
                ]
            }
        ]

        for r_data in regions_data:
            region = db.session.query(Region).filter_by(name=r_data["name"]).first()
            if not region:
                region = Region(name=r_data["name"])
                db.session.add(region)
                db.session.commit() # Commit to get region.id
            
            for f_name in r_data["facilities"]:
                facility = db.session.query(Facility).filter_by(name=f_name, region_id=region.id).first()
                if not facility:
                    facility = Facility(name=f_name, region_id=region.id)
                    db.session.add(facility)
        
        db.session.commit()
        print("Database seeded successfully with sample regions and facilities.")

if __name__ == "__main__":
    seed()
