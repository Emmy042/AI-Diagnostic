import os
from app.web import create_app
from app.models import db, Region, Facility

def seed():
    # Set to demo mode so we don't try to load the ML model just to seed the DB
    os.environ["DERMA_DEMO_MODE"] = "True"
    app = create_app()
    with app.app_context():
        regions_data = [
            {"name": "Abia", "facilities": ["Federal Medical Centre, Umuahia", "Abia State University Teaching Hospital"]},
            {"name": "Adamawa", "facilities": ["Federal Medical Centre, Yola", "Specialist Hospital Yola"]},
            {"name": "Akwa Ibom", "facilities": ["University of Uyo Teaching Hospital", "Ibom Multi-Specialist Hospital"]},
            {"name": "Anambra", "facilities": ["Nnamdi Azikiwe University Teaching Hospital", "Chukwuemeka Odumegwu Ojukwu University Teaching Hospital"]},
            {"name": "Bauchi", "facilities": ["Abubakar Tafawa Balewa University Teaching Hospital", "Federal Medical Centre, Azare"]},
            {"name": "Bayelsa", "facilities": ["Federal Medical Centre, Yenagoa", "Niger Delta University Teaching Hospital"]},
            {"name": "Benue", "facilities": ["Federal Medical Centre, Makurdi", "Benue State University Teaching Hospital"]},
            {"name": "Borno", "facilities": ["University of Maiduguri Teaching Hospital", "State Specialist Hospital Maiduguri"]},
            {"name": "Cross River", "facilities": ["University of Calabar Teaching Hospital", "Federal Neuro Psychiatric Hospital Calabar"]},
            {"name": "Delta", "facilities": ["Federal Medical Centre, Asaba", "Delta State University Teaching Hospital, Oghara"]},
            {"name": "Ebonyi", "facilities": ["Alex Ekwueme Federal University Teaching Hospital"]},
            {"name": "Edo", "facilities": ["University of Benin Teaching Hospital", "Irrua Specialist Teaching Hospital"]},
            {"name": "Ekiti", "facilities": ["Federal Teaching Hospital, Ido-Ekiti", "Ekiti State University Teaching Hospital"]},
            {"name": "Enugu", "facilities": ["University of Nigeria Teaching Hospital", "Enugu State University Teaching Hospital"]},
            {"name": "FCT Abuja", "facilities": ["National Hospital Abuja", "Garki Hospital", "Asokoro District Hospital", "Maitama District Hospital"]},
            {"name": "Gombe", "facilities": ["Federal Teaching Hospital, Gombe", "State Specialist Hospital Gombe"]},
            {"name": "Imo", "facilities": ["Federal Medical Centre, Owerri", "Imo State University Teaching Hospital"]},
            {"name": "Jigawa", "facilities": ["Federal Medical Centre, Birnin Kudu", "Rasheed Shekoni Specialist Hospital"]},
            {"name": "Kaduna", "facilities": ["Ahmadu Bello University Teaching Hospital", "National Ear Care Centre", "Barau Dikko Teaching Hospital"]},
            {"name": "Kano", "facilities": ["Aminu Kano Teaching Hospital", "Murtala Muhammed Specialist Hospital", "National Orthopaedic Hospital, Dala"]},
            {"name": "Katsina", "facilities": ["Federal Medical Centre, Katsina", "General Hospital Katsina"]},
            {"name": "Kebbi", "facilities": ["Federal Medical Centre, Birnin Kebbi", "Sir Yahaya Memorial Hospital"]},
            {"name": "Kogi", "facilities": ["Federal Medical Centre, Lokoja", "Kogi State Specialist Hospital"]},
            {"name": "Kwara", "facilities": ["University of Ilorin Teaching Hospital", "General Hospital Ilorin"]},
            {"name": "Lagos", "facilities": ["Lagos University Teaching Hospital (LUTH)", "Lagos State University Teaching Hospital (LASUTH)", "General Hospital, Lagos", "National Orthopaedic Hospital Igbobi"]},
            {"name": "Nasarawa", "facilities": ["Federal Medical Centre, Keffi", "Dalhatu Araf Specialist Hospital"]},
            {"name": "Niger", "facilities": ["Federal Medical Centre, Bida", "General Hospital Minna"]},
            {"name": "Ogun", "facilities": ["Olabisi Onabanjo University Teaching Hospital", "Federal Medical Centre, Abeokuta"]},
            {"name": "Ondo", "facilities": ["Federal Medical Centre, Owo", "University of Medical Sciences Teaching Hospital"]},
            {"name": "Osun", "facilities": ["Obafemi Awolowo University Teaching Hospital", "Osun State University Teaching Hospital"]},
            {"name": "Oyo", "facilities": ["University College Hospital (UCH) Ibadan", "Adeoyo Maternity Teaching Hospital"]},
            {"name": "Plateau", "facilities": ["Jos University Teaching Hospital (JUTH)", "Plateau State Specialist Hospital"]},
            {"name": "Rivers", "facilities": ["University of Port Harcourt Teaching Hospital", "Rivers State University Teaching Hospital"]},
            {"name": "Sokoto", "facilities": ["Usmanu Danfodiyo University Teaching Hospital", "Specialist Hospital Sokoto"]},
            {"name": "Taraba", "facilities": ["Federal Medical Centre, Jalingo", "State Specialist Hospital Jalingo"]},
            {"name": "Yobe", "facilities": ["Federal Medical Centre, Nguru", "Sani Abacha Specialist Hospital Damaturu"]},
            {"name": "Zamfara", "facilities": ["Federal Medical Centre, Gusau", "Ahmad Sani Yariman Bakura Specialist Hospital"]}
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
        print("Database seeded successfully with all 36 states and FCT facilities.")

if __name__ == "__main__":
    seed()
