"""
JAL-DRISHTI — Groundwater Data Seed Script (Legacy)
===================================================
This script was used during early development to generate synthetic data
for UI testing. It should NOT be used with the production database.

Production data is sourced directly from CGWB (Central Ground Water Board)
National Compilation publications and imported via import_ingres_data.py.

Usage:
    python seed_groundwater.py          # Seeds the database (development only)
    python seed_groundwater.py --reset  # Drops and re-seeds (development only)
"""

import sys
import os
import random
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base, GroundWater

# ─── All Indian States & UTs with Districts and Blocks ──────────────────────

STATES_DISTRICTS_BLOCKS = {
    # ─── States ──────────────────────────────────────────────────────────────
    "Andhra Pradesh": {
        "Guntur": ["Tenali", "Mangalagiri", "Sattenapalli"],
        "Krishna": ["Machilipatnam", "Gudivada", "Nuzvid"],
        "West Godavari": ["Narsapur", "Tadepalligudem", "Bhimavaram"],
        "Chittoor": ["Tirupati", "Chittoor", "Madanapalle"],
    },
    "Arunachal Pradesh": {
        "Itanagar": ["Itanagar", "Banderdawa", "Naharlagun"],
        "Tawang": ["Tawang", "Lumla", "Kitpi"],
        "Pasighat": ["Pasighat", "Mebo", "Ruksin"],
    },
    "Assam": {
        "Guwahati": ["Dispur", "Chandrapur", "Azara"],
        "Dibrugarh": ["Dibrugarh", "Chabua", "Tingkhong"],
        "Jorhat": ["Jorhat", "Majuli", "Teok"],
        "Silchar": ["Silchar", "Katigorah", "Lakhipur"],
    },
    "Bihar": {
        "Patna": ["Patna", "Danapur", "Phulwari", "Masaurhi"],
        "Gaya": ["Gaya", "Bodh Gaya", "Tekari", "Imamganj"],
        "Muzaffarpur": ["Muzaffarpur", "Sitamarhi", "Sheohar"],
        "Bhagalpur": ["Bhagalpur", "Naugachia", "Kahalgaon"],
    },
    "Chhattisgarh": {
        "Raipur": ["Raipur", "Arang", "Abhanpur", "Tilda"],
        "Bilaspur": ["Bilaspur", "Bilha", "Kota", "Masturi"],
        "Durg": ["Durg", "Bhilai", "Rajnandgaon", "Dongargarh"],
        "Jagdalpur": ["Jagdalpur", "Bastar", "Dantewada"],
    },
    "Goa": {
        "North Goa": ["Mapusa", "Calangute", "Ponda", "Bicholim"],
        "South Goa": ["Margao", "Vasco", "Quepem", "Sanguem"],
    },
    "Gujarat": {
        "Ahmedabad": ["Daskroi", "Dholka", "Bavla", "Sanand"],
        "Surat": ["Uchchhal", "Mahuva", "Bardoli"],
        "Rajkot": ["Gondal", "Jetpur", "Dhoraji", "Upleta"],
        "Junagadh": ["Mangrol", "Junagadh", "Veraval"],
    },
    "Haryana": {
        "Karnal": ["Assandh", "Indri", "Nissing", "Gharaunda"],
        "Hisar": ["Hisar", "Uklana", "Narnaund", "Loharu"],
        "Rohtak": ["Rohtak", "Bahadurgarh", "Jhajjar", "Kalanaur"],
        "Gurgaon": ["Gurgaon", "Pataudi", "Farrukhnagar", "Sohna"],
    },
    "Himachal Pradesh": {
        "Shimla": ["Shimla", "Theog", "Kotkhai", "Rampur"],
        "Mandi": ["Mandi", "Sundernagar", "Jogindernagar", "Karsog"],
        "Kangra": ["Dharamshala", "Kangra", "Palampur", "Nagrota"],
        "Kullu": ["Kullu", "Manali", "Bhuntar", "Anni"],
    },
    "Jharkhand": {
        "Ranchi": ["Ranchi", "Kanke", "Namkum", "Ormanjhi"],
        "Jamshedpur": ["Jubilee", "Sonari", "Gamharia", "Dimna"],
        "Dhanbad": ["Dhanbad", "Jharia", "Tisri", "Baghmara"],
        "Bokaro": ["Bokaro", "Chas", "Petroia", "Kasmar"],
    },
    "Karnataka": {
        "Bengaluru Rural": ["Devanahalli", "Hoskote", "Nelamangala", "Bidadi"],
        "Mysuru": ["T Narsipur", "Hunsur", "Krishnarajanagar", "Periyapatna"],
        "Raichur": ["Sindhanur", "Manvi", "Lingasugur", "Yadgir"],
        "Belgaum": ["Ramdurg", "Belgaum", "Gokak", "Hukkeri"],
    },
    "Kerala": {
        "Thiruvananthapuram": ["Nedumangad", "Attingal", "Neyyattinkara", "Vattiyoorkavu"],
        "Ernakulam": ["Aluva", "Perumbavoor", "Kothamangalam", "Muvattupuzha"],
        "Thrissur": ["Chalakudy", "Kodungallur", "Irinjalakuda", "Wadakkanchery"],
        "Kozhikode": ["Kozhikode", "Vadakara", "Koyilandy", "Quilandy"],
    },
    "Madhya Pradesh": {
        "Bhopal": ["Bhopal", "Berasia", "Kolar", "Huzur"],
        "Indore": ["Indore", "Mhow", "Depalpur", "Sanwer"],
        "Jabalpur": ["Jabalpur", "Panagar", "Sihora", "Mandla"],
        "Gwalior": ["Gwalior", "Dabra", "Bhitarwar", "Chinour"],
    },
    "Maharashtra": {
        "Pune": ["Mulshi", "Maval", "Haveli", "Baramati"],
        "Nagpur": ["Kamptee", "Katol", "Saoner", "Hingna"],
        "Nashik": ["Sinnar", "Niphad", "Yevla", "Chandwad"],
        "Mumbai": ["Andheri", "Borivali", "Kurla", "Thane"],
    },
    "Manipur": {
        "Imphal": ["Imphal West", "Imphal East", "Thoubal", "Bishnupur"],
        "Churachandpur": ["Churachandpur", "Henglep", "Chingai"],
    },
    "Meghalaya": {
        "Shillong": ["East Khasi Hills", "West Khasi Hills", "South West Khasi Hills"],
        "Tura": ["West Garo Hills", "East Garo Hills", "South Garo Hills"],
    },
    "Mizoram": {
        "Aizawl": ["Aizawl", "Sairang", "Tlungvel"],
        "Lunglei": ["Lunglei", "Hnahthial", "Siaha"],
    },
    "Nagaland": {
        "Kohima": ["Kohima", "Jakhama", "Kezocha"],
        "Dimapur": ["Dimapur", "Chumukedima", "Medziphema"],
    },
    "Odisha": {
        "Bhubaneswar": ["Bhubaneswar", "Khurda", "Jatni", "Tangi"],
        "Cuttack": ["Cuttack", "Niali", "Kandarpur", "Banki"],
        "Sambalpur": ["Sambalpur", "Burla", "Hirakud", "Rengali"],
        "Berhampur": ["Berhampur", "Chhatrapur", "Bhanjanagar"],
    },
    "Punjab": {
        "Ludhiana": ["Khanna", "Samrala", "Payal", "Raikot"],
        "Amritsar": ["Tarn Taran", "Batala", "Ajnala", "Majitha"],
        "Patiala": ["Rajpura", "Samana", "Nabha", "Ghagga"],
        "Jalandhar": ["Phillaur", "Jalandhar", "Nakodar", "Lohian Khas"],
    },
    "Rajasthan": {
        "Jaipur": ["Amber", "Bagru", "Chomu", "Sanganer"],
        "Jodhpur": ["Bilara", "Luni", "Shergarh", "Phalodi"],
        "Udaipur": ["Gogunda", "Kotda", "Sarada", "Vallabhnagar"],
        "Kota": ["Ladpura", "Sangod", "Chipabarod"],
    },
    "Sikkim": {
        "Gangtok": ["Gangtok", "Rangpo", "Singtam"],
        "Namchi": ["Namchi", "Jorethang", "Ravongla"],
    },
    "Tamil Nadu": {
        "Coimbatore": ["Mettupalayam", "Sulur", "Pollachi", "Valparai"],
        "Madurai": ["Vadipatti", "Usilampatti", "Melur", "Peraiyur"],
        "Trichy": ["Lalgudi", "Musiri", "Thuraiyur", "Marungapuri"],
        "Erode": ["Bhavani", "Gobichettipalayam", "Sathyamangalam"],
    },
    "Telangana": {
        "Hyderabad": ["Secunderabad", "Malkajgiri", "Uppal", "L B Nagar"],
        "Warangal": ["Warangal", "Hanamkonda", "Narsampet", "Parkal"],
        "Karimnagar": ["Karimnagar", "Huzurabad", "Jammikunta", "Sircilla"],
        "Nizamabad": ["Nizamabad", "Bodhan", "Kamareddy", "Banswada"],
    },
    "Tripura": {
        "Agartala": ["Agartala", "Mohanpur", "Bishalgarh", "Jirania"],
        "Udaipur": ["Udaipur", "Ambedkar Nagar", "Kathaltali"],
    },
    "Uttar Pradesh": {
        "Lucknow": ["Malihabad", "Bakshi Ka Talarab", "Mohanlalganj", "Gosaiganj"],
        "Agra": ["Etmadpur", "Fatehabad", "Kheragarh", "Bah"],
        "Varanasi": ["Cholapur", "Arazi", "Harhua", "Kashi"],
        "Kanpur": ["Bilhaur", "Kanpur", "Bithoor", "Ghatampur"],
    },
    "Uttarakhand": {
        "Dehradun": ["Dehradun", "Mussoorie", "Doiwala", "Rishikesh"],
        "Haridwar": ["Haridwar", "Roorkee", "Laksar", "Bhagwanpur"],
        "Nainital": ["Haldwani", "Kathgodam", "Ramnagar", "Bhimtal"],
    },
    "West Bengal": {
        "Burdwan": ["Katwa", "Kalna", "Memari", "Manteswar"],
        "Hooghly": ["Chinsurah", "Arambag", "Goghat", "Tarakeswar"],
        "Nadia": ["Ranaghat", "Krishnanagar", "Tehatta", "Chakdaha"],
        "Kolkata": ["Alipore", "Ballygunge", "Salt Lake", "New Town"],
    },

    # ─── Union Territories ───────────────────────────────────────────────────
    "Delhi": {
        "New Delhi": ["Civil Lines", "Karol Bagh", "Defence Colony", "Dwarka"],
        "Central Delhi": ["Daryaganj", "Paharganj", "Karol Bagh"],
        "South Delhi": ["Saket", "Lajpat Nagar", "Greater Kailash"],
    },
    "Jammu & Kashmir": {
        "Srinagar": ["Srinagar", "Budgam", "Ganderbal", "Pampore"],
        "Jammu": ["Jammu", "Kathua", "Samba", "Udhampur"],
        "Anantnag": ["Anantnag", "Kulgam", "Shopian", "Pulwama"],
    },
    "Ladakh": {
        "Leh": ["Leh", "Nubra", "Changthang"],
        "Kargil": ["Kargil", "Shakar Chiktan", "Suru"],
    },
    "Chandigarh": {
        "Chandigarh": ["Chandigarh", "Manimajra", "Mauli Jagran"],
    },
    "Puducherry": {
        "Puducherry": ["Puducherry", "Oulgaret", "Villianur"],
        "Karaikal": ["Karaikal", "Thirunallar", "Nedumbassery"],
    },
    "Andaman & Nicobar Islands": {
        "South Andaman": ["Port Blair", "Ferrargunj", "Little Andaman"],
    },
    "Dadra & Nagar Haveli and Daman & Diu": {
        "Daman": ["Daman", "Diu", "Silvassa"],
    },
    "Lakshadweep": {
        "Kavaratti": ["Kavaratti", "Agatti", "Minicoy"],
    },
}

# ─── Latitude/longitude center points per state (approximate) ───────────────

STATE_COORDS = {
    "Andhra Pradesh": (15.9, 79.7),
    "Arunachal Pradesh": (28.2, 94.7),
    "Assam": (26.2, 92.9),
    "Bihar": (25.6, 85.1),
    "Chhattisgarh": (21.3, 82.0),
    "Goa": (15.4, 74.0),
    "Gujarat": (22.3, 71.5),
    "Haryana": (29.0, 76.0),
    "Himachal Pradesh": (31.1, 77.2),
    "Jharkhand": (23.6, 85.3),
    "Karnataka": (15.0, 76.0),
    "Kerala": (10.8, 76.2),
    "Madhya Pradesh": (22.9, 78.6),
    "Maharashtra": (19.5, 74.5),
    "Manipur": (24.7, 93.9),
    "Meghalaya": (25.5, 91.9),
    "Mizoram": (23.2, 92.7),
    "Nagaland": (26.2, 94.6),
    "Odisha": (20.9, 85.3),
    "Punjab": (31.0, 75.5),
    "Rajasthan": (26.9, 72.0),
    "Sikkim": (27.5, 88.5),
    "Tamil Nadu": (11.0, 78.5),
    "Telangana": (17.1, 79.2),
    "Tripura": (23.9, 91.9),
    "Uttar Pradesh": (26.8, 80.0),
    "Uttarakhand": (30.1, 79.0),
    "West Bengal": (23.0, 87.5),
    "Delhi": (28.6, 77.2),
    "Jammu & Kashmir": (33.8, 74.9),
    "Ladakh": (34.2, 77.6),
    "Chandigarh": (30.7, 76.8),
    "Puducherry": (11.9, 79.8),
    "Andaman & Nicobar Islands": (11.7, 92.7),
    "Dadra & Nagar Haveli and Daman & Diu": (20.4, 72.9),
    "Lakshadweep": (10.6, 72.6),
}


def generate_block_data(state, district, block, lat_center, lng_center):
    """Generate 5 years of realistic groundwater data for a block."""
    records = []

    # Base parameters vary by region
    base_recharge = random.uniform(200, 1200)
    base_resource = random.uniform(150, 900)
    base_extraction = random.uniform(100, 800)

    # Offset lat/lng per block
    lat = round(lat_center + random.uniform(-1.5, 1.5), 4)
    lng = round(lng_center + random.uniform(-2.0, 2.0), 4)

    for year in range(2020, 2025):
        # Year-over-year variation
        year_factor = 1 + random.uniform(-0.08, 0.08) * (year - 2022)
        recharge = round(base_recharge * year_factor + random.uniform(-30, 30), 2)
        resource = round(base_resource * year_factor + random.uniform(-20, 20), 2)
        extraction = round(base_extraction * year_factor + random.uniform(-40, 40), 2)

        # Ensure extraction doesn't exceed resource by too much
        extraction = min(extraction, resource * 1.3)

        # Extraction stage
        stage = round((extraction / resource * 100), 2) if resource > 0 else 0

        # Category based on stage
        if stage < 70:
            category = "Safe"
        elif stage < 90:
            category = "Semi-Critical"
        elif stage < 100:
            category = "Critical"
        else:
            category = "Over-Exploited"

        records.append({
            "state": state,
            "district": district,
            "block": block,
            "assessment_year": year,
            "annual_groundwater_recharge": recharge,
            "extractable_groundwater_resource": resource,
            "groundwater_extraction": extraction,
            "extraction_stage": stage,
            "category": category,
            "latitude": lat,
            "longitude": lng,
            "is_demo_data": 1,
        })

    return records


def seed(reset=False):
    """Seed the database with demo data."""
    from database import SessionLocal

    if reset:
        print("Dropping and recreating groundwater table...")
        GroundWater.__table__.drop(bind=engine, checkfirst=True)
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    existing = db.query(GroundWater).count()
    if existing > 0 and not reset:
        print(f"Database already has {existing} records. Use --reset to re-seed.")
        db.close()
        return

    all_records = []
    block_count = 0

    for state, districts in STATES_DISTRICTS_BLOCKS.items():
        lat_center, lng_center = STATE_COORDS.get(state, (22.0, 80.0))
        for district, blocks in districts.items():
            for block in blocks:
                block_count += 1
                records = generate_block_data(state, district, block, lat_center, lng_center)
                all_records.extend(records)

    # Bulk insert
    db.bulk_insert_mappings(GroundWater, all_records)
    db.commit()
    db.close()

    total = len(all_records)
    states_count = len(STATES_DISTRICTS_BLOCKS)
    districts_count = sum(len(d) for d in STATES_DISTRICTS_BLOCKS.values())
    print(f"Seeded {block_count} blocks × 5 years = {total} groundwater records")
    print(f"States/UTs: {states_count}")
    print(f"Districts: {districts_count}")
    print(f"Years: 2020–2024")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed groundwater demo data")
    parser.add_argument("--reset", action="store_true", help="Drop and re-seed")
    args = parser.parse_args()
    seed(reset=args.reset)
