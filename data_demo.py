import pandas as pd
from datetime import datetime, timedelta

# Blood groups and components
BLOOD_GROUPS = ["All Blood Groups", "A+", "A−", "B+", "B−", "AB+", "AB−", "O+", "O−"]
BLOOD_COMPONENTS = ["All Components", "Packed Red Blood Cells", "Whole Blood", "Platelets", "Plasma"]
KERALA_DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha", "Kottayam",
    "Idukki", "Ernakulam", "Thrissur", "Malappuram", "Kozhikode",
    "Wayanad", "Kannur", "Kasaragod"
]

# Comprehensive hospital database for Kerala
BLOOD_BANKS = pd.DataFrame([
    # ==================== ERNAKULAM DISTRICT (15 hospitals) ====================
    {
        "id": "BB_EKM_001",
        "name": "Ernakulam General Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Hospital Rd, Fort Kochi, Ernakulam 682001",
        "phone": "+91-484-2203201",
        "coordinates": "9.9673,76.2583",
        "google_maps_link": "https://www.google.com/maps/search/Ernakulam+General+Hospital+Blood+Bank/@9.9673,76.2583,15z"
    },
    {
        "id": "BB_EKM_002",
        "name": "Lakeshore Hospital Blood Bank - Kochi",
        "district": "Ernakulam",
        "address": "Maradu, Kochi 682304",
        "phone": "+91-484-6725000",
        "coordinates": "9.9500,76.3288",
        "google_maps_link": "https://www.google.com/maps/search/Lakeshore+Hospital+Kochi/@9.9500,76.3288,15z"
    },
    {
        "id": "BB_EKM_003",
        "name": "Red Cross Blood Bank - Kaloor",
        "district": "Ernakulam",
        "address": "Red Cross Society, Kaloor, Kochi 682017",
        "phone": "+91-484-2377988",
        "coordinates": "9.9876,76.3012",
        "google_maps_link": "https://www.google.com/maps/search/Red+Cross+Blood+Bank+Kaloor/@9.9876,76.3012,15z"
    },
    {
        "id": "BB_EKM_004",
        "name": "Amrita Institute of Medical Sciences Blood Bank",
        "district": "Ernakulam",
        "address": "Elamakkara, Kochi 682026",
        "phone": "+91-484-2805100",
        "coordinates": "9.9850,76.2950",
        "google_maps_link": "https://www.google.com/maps/search/Amrita+Institute+Blood+Bank+Kochi/@9.9850,76.2950,15z"
    },
    {
        "id": "BB_EKM_005",
        "name": "Rajagiri Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Chunangamveli, Kochi 682033",
        "phone": "+91-484-2812000",
        "coordinates": "9.9700,76.3100",
        "google_maps_link": "https://www.google.com/maps/search/Rajagiri+Hospital+Kochi/@9.9700,76.3100,15z"
    },
    {
        "id": "BB_EKM_006",
        "name": "Cochin Shipyard Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Cochin Shipyard, Kochi 682009",
        "phone": "+91-484-2668511",
        "coordinates": "9.9450,76.2850",
        "google_maps_link": "https://www.google.com/maps/search/Cochin+Shipyard+Hospital/@9.9450,76.2850,15z"
    },
    {
        "id": "BB_EKM_007",
        "name": "PVS Memorial Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Palarivattom, Kochi 682025",
        "phone": "+91-484-2345678",
        "coordinates": "9.9780,76.3150",
        "google_maps_link": "https://www.google.com/maps/search/PVS+Memorial+Hospital+Kochi/@9.9780,76.3150,15z"
    },
    {
        "id": "BB_EKM_008",
        "name": "Sunrise Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Kakkanad, Kochi 682037",
        "phone": "+91-484-2960000",
        "coordinates": "10.0100,76.3200",
        "google_maps_link": "https://www.google.com/maps/search/Sunrise+Hospital+Kochi/@10.0100,76.3200,15z"
    },
    {
        "id": "BB_EKM_009",
        "name": "AIMS Blood Bank - Palarivattom",
        "district": "Ernakulam",
        "address": "Palarivattom, Kochi 682025",
        "phone": "+91-484-4002020",
        "coordinates": "9.9800,76.3140",
        "google_maps_link": "https://www.google.com/maps/search/AIMS+Palarivattom+Kochi/@9.9800,76.3140,15z"
    },
    {
        "id": "BB_EKM_010",
        "name": "VPS Lakeshore Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Maradu, Kochi 682304",
        "phone": "+91-484-4018000",
        "coordinates": "9.9520,76.3280",
        "google_maps_link": "https://www.google.com/maps/search/VPS+Lakeshore+Hospital+Maradu/@9.9520,76.3280,15z"
    },
    {
        "id": "BB_EKM_011",
        "name": "Kalamassery Medical Centre Blood Bank",
        "district": "Ernakulam",
        "address": "Kalamassery, Kochi 683104",
        "phone": "+91-484-2877777",
        "coordinates": "10.0200,76.2700",
        "google_maps_link": "https://www.google.com/maps/search/Kalamassery+Medical+Centre/@10.0200,76.2700,15z"
    },
    {
        "id": "BB_EKM_012",
        "name": "Lisie Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Kacheripady, Kochi 682018",
        "phone": "+91-484-2305050",
        "coordinates": "9.9650,76.2950",
        "google_maps_link": "https://www.google.com/maps/search/Lisie+Hospital+Kochi/@9.9650,76.2950,15z"
    },
    {
        "id": "BB_EKM_013",
        "name": "Holy Family Hospital Blood Bank",
        "district": "Ernakulam",
        "address": "Ernakulathappan Lane, Kochi 682018",
        "phone": "+91-484-2352525",
        "coordinates": "9.9670,76.2970",
        "google_maps_link": "https://www.google.com/maps/search/Holy+Family+Hospital+Kochi/@9.9670,76.2970,15z"
    },
    {
        "id": "BB_EKM_014",
        "name": "Aster Medcity Blood Bank",
        "district": "Ernakulam",
        "address": "Kochi 682035",
        "phone": "+91-484-6166666",
        "coordinates": "10.0050,76.3450",
        "google_maps_link": "https://www.google.com/maps/search/Aster+Medcity+Kochi/@10.0050,76.3450,15z"
    },
    {
        "id": "BB_EKM_015",
        "name": "Government Hospital Ernakulathappan Lane",
        "district": "Ernakulam",
        "address": "Ernakulathappan Lane, Kochi 682018",
        "phone": "+91-484-2203300",
        "coordinates": "9.9675,76.2965",
        "google_maps_link": "https://www.google.com/maps/search/Government+Hospital+Ernakulathappan+Lane/@9.9675,76.2965,15z"
    },
    
    # ==================== OTHER DISTRICTS (Sample) ====================
    {
        "id": "BB001",
        "name": "Trivandrum Medical College Blood Bank",
        "district": "Thiruvananthapuram",
        "address": "Medical College Rd, Thiruvananthapuram 695011",
        "phone": "+91-471-2552081",
        "coordinates": "8.5241,76.9366",
        "google_maps_link": "https://www.google.com/maps/search/Trivandrum+Medical+College+Blood+Bank/@8.5241,76.9366,15z"
    },
    {
        "id": "BB002",
        "name": "Kottayam Medical College Blood Bank",
        "district": "Kottayam",
        "address": "Medical College Campus, Kottayam 686008",
        "phone": "+91-481-2560600",
        "coordinates": "9.5936,76.5261",
        "google_maps_link": "https://www.google.com/maps/search/Kottayam+Medical+College+Blood+Bank/@9.5936,76.5261,15z"
    },
    {
        "id": "BB004",
        "name": "Thrissur Medical College Blood Bank",
        "district": "Thrissur",
        "address": "Medical College, Thrissur 680596",
        "phone": "+91-487-2345678",
        "coordinates": "10.5669,76.2144",
        "google_maps_link": "https://www.google.com/maps/search/Thrissur+Medical+College+Blood+Bank/@10.5669,76.2144,15z"
    },
    {
        "id": "BB005",
        "name": "Kozhikode Medical College Blood Bank",
        "district": "Kozhikode",
        "address": "Medical College Campus, Kozhikode 673008",
        "phone": "+91-495-2368800",
        "coordinates": "11.2588,75.8355",
        "google_maps_link": "https://www.google.com/maps/search/Kozhikode+Medical+College+Blood+Bank/@11.2588,75.8355,15z"
    },
    {
        "id": "BB006",
        "name": "Kannur Medical College Blood Bank",
        "district": "Kannur",
        "address": "Medical College Rd, Kannur 670612",
        "phone": "+91-497-2902111",
        "coordinates": "12.1833,75.3667",
        "google_maps_link": "https://www.google.com/maps/search/Kannur+Medical+College+Blood+Bank/@12.1833,75.3667,15z"
    },
    {
        "id": "BB008",
        "name": "Alappuzha District Hospital Blood Bank",
        "district": "Alappuzha",
        "address": "Govt Hospital, Alappuzha 688011",
        "phone": "+91-477-2266900",
        "coordinates": "9.4862,76.3272",
        "google_maps_link": "https://www.google.com/maps/search/Alappuzha+District+Hospital/@9.4862,76.3272,15z"
    },
])

# Sample blood stock (demo data - not real)
today = datetime.now().strftime("%Y-%m-%d")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

# Helper function to generate realistic stock data
def generate_stock(hospital_id, blood_groups_list):
    """Generate stock data for a hospital across multiple blood groups and components"""
    stock_records = []
    components_list = ["Packed Red Blood Cells", "Whole Blood", "Platelets", "Plasma"]
    
    for bg in blood_groups_list:
        for component in components_list:
            # Randomly assign stock status
            import random
            rand = random.random()
            if rand < 0.1:  # 10% chance: not verified
                units = 0
                status = "not_verified"
            elif rand < 0.2:  # 10% chance: out of stock
                units = 0
                status = "verified"
            elif rand < 0.3:  # 10% chance: low stock
                units = random.randint(1, 4)
                status = "verified"
            else:  # 70% chance: available
                units = random.randint(8, 25)
                status = "verified"
            
            stock_records.append({
                "hospital_id": hospital_id,
                "blood_group": bg,
                "component": component,
                "units_available": units,
                "expiry_date": next_week if units > 0 else "2026-10-19",
                "update_time": today,
                "source": "eRaktKosh",
                "verification_status": status
            })
    
    return stock_records

BLOOD_STOCK_LIST = []

# Generate stock for all Ernakulam hospitals
ernakulam_hospitals = [
    "BB_EKM_001", "BB_EKM_002", "BB_EKM_003", "BB_EKM_004", "BB_EKM_005",
    "BB_EKM_006", "BB_EKM_007", "BB_EKM_008", "BB_EKM_009", "BB_EKM_010",
    "BB_EKM_011", "BB_EKM_012", "BB_EKM_013", "BB_EKM_014", "BB_EKM_015"
]

blood_groups_all = ["O+", "O−", "A+", "A−", "B+", "B−", "AB+", "AB−"]

for hospital in ernakulam_hospitals:
    BLOOD_STOCK_LIST.extend(generate_stock(hospital, blood_groups_all))

# Add sample data for other districts
BLOOD_STOCK_LIST.extend([
    # Trivandrum
    {"hospital_id": "BB001", "blood_group": "O+", "component": "Packed Red Blood Cells", "units_available": 12, "expiry_date": next_week, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    {"hospital_id": "BB001", "blood_group": "A+", "component": "Plasma", "units_available": 8, "expiry_date": next_week, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    {"hospital_id": "BB001", "blood_group": "B+", "component": "Whole Blood", "units_available": 3, "expiry_date": tomorrow, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    
    # Kottayam
    {"hospital_id": "BB002", "blood_group": "O+", "component": "Packed Red Blood Cells", "units_available": 18, "expiry_date": next_week, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    {"hospital_id": "BB002", "blood_group": "A+", "component": "Platelets", "units_available": 6, "expiry_date": tomorrow, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    
    # Thrissur
    {"hospital_id": "BB004", "blood_group": "A+", "component": "Packed Red Blood Cells", "units_available": 14, "expiry_date": next_week, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    {"hospital_id": "BB004", "blood_group": "O+", "component": "Platelets", "units_available": 9, "expiry_date": tomorrow, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    
    # Kozhikode
    {"hospital_id": "BB005", "blood_group": "O+", "component": "Packed Red Blood Cells", "units_available": 16, "expiry_date": next_week, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    {"hospital_id": "BB005", "blood_group": "B+", "component": "Whole Blood", "units_available": 11, "expiry_date": next_week, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    
    # Kannur
    {"hospital_id": "BB006", "blood_group": "A+", "component": "Platelets", "units_available": 4, "expiry_date": tomorrow, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
    
    # Alappuzha
    {"hospital_id": "BB008", "blood_group": "O+", "component": "Packed Red Blood Cells", "units_available": 13, "expiry_date": next_week, "update_time": today, "source": "eRaktKosh", "verification_status": "verified"},
])

BLOOD_STOCK = pd.DataFrame(BLOOD_STOCK_LIST)
