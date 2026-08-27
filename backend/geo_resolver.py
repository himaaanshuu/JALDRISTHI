"""
Geographic Entity Resolution for Indian Groundwater Intelligence.
Resolves abbreviations, aliases, and common names to canonical entities.
"""

from typing import Dict, List, Optional, Tuple

# ─── Canonical State/UT Names ──────────────────────────────────────────────

STATE_CANONICAL: Dict[str, str] = {
    "andhra pradesh": "Andhra Pradesh", "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam", "bihar": "Bihar", "chhattisgarh": "Chhattisgarh",
    "goa": "Goa", "gujarat": "Gujarat", "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh", "jharkhand": "Jharkhand",
    "karnataka": "Karnataka", "kerala": "Kerala",
    "madhya pradesh": "Madhya Pradesh", "maharashtra": "Maharashtra",
    "manipur": "Manipur", "meghalaya": "Meghalaya", "mizoram": "Mizoram",
    "nagaland": "Nagaland", "odisha": "Odisha", "punjab": "Punjab",
    "rajasthan": "Rajasthan", "sikkim": "Sikkim", "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana", "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh", "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal",
    "delhi": "Delhi", "new delhi": "Delhi",
    "jammu and kashmir": "Jammu & Kashmir", "jammu & kashmir": "Jammu & Kashmir",
    "j&k": "Jammu & Kashmir", "j and k": "Jammu & Kashmir",
    "ladakh": "Ladakh",
    "chandigarh": "Chandigarh",
    "puducherry": "Puducherry", "pondicherry": "Puducherry",
    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "andaman & nicobar islands": "Andaman & Nicobar Islands",
    "andaman & nicobar": "Andaman & Nicobar Islands",
    "a&n islands": "Andaman & Nicobar Islands",
    "lakshadweep": "Lakshadweep",
    "dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra & nagar haveli and daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dnhdd": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
}

# ─── Abbreviations ──────────────────────────────────────────────────────────

STATE_ABBREVIATIONS: Dict[str, str] = {
    "ap": "Andhra Pradesh", "ar": "Arunachal Pradesh", "as": "Assam",
    "br": "Bihar", "cg": "Chhattisgarh", "ga": "Goa", "gj": "Gujarat",
    "hr": "Haryana", "hp": "Himachal Pradesh", "jh": "Jharkhand",
    "ka": "Karnataka", "kl": "Kerala", "mp": "Madhya Pradesh",
    "mh": "Maharashtra", "mn": "Manipur", "ml": "Meghalaya",
    "mz": "Mizoram", "nl": "Nagaland", "od": "Odisha", "or": "Odisha",
    "pb": "Punjab", "rj": "Rajasthan", "sk": "Sikkim", "tn": "Tamil Nadu",
    "ts": "Telangana", "tr": "Tripura", "up": "Uttar Pradesh",
    "uk": "Uttarakhand", "wb": "West Bengal", "ut": "Uttarakhand",
}

# ─── Hindi Names ────────────────────────────────────────────────────────────

STATE_HINDI: Dict[str, str] = {
    "आंध्र प्रदेश": "Andhra Pradesh", "अरुणाचल प्रदेश": "Arunachal Pradesh",
    "असम": "Assam", "बिहार": "Bihar", "छत्तीसगढ़": "Chhattisgarh",
    "गोवा": "Goa", "गुजरात": "Gujarat", "हरियाणा": "Haryana",
    "हिमाचल प्रदेश": "Himachal Pradesh", "झारखंड": "Jharkhand",
    "कर्नाटक": "Karnataka", "केरल": "Kerala",
    "मध्य प्रदेश": "Madhya Pradesh", "महाराष्ट्र": "Maharashtra",
    "मणिपुर": "Manipur", "मेघालय": "Meghalaya", "मिज़ोरम": "Mizoram",
    "नागालैंड": "Nagaland", "ओडिशा": "Odisha", "पंजाब": "Punjab",
    "राजस्थान": "Rajasthan", "सिक्किम": "Sikkim", "तमिल नाडु": "Tamil Nadu",
    "तेलंगाना": "Telangana", "त्रिपुरा": "Tripura",
    "उत्तर प्रदेश": "Uttar Pradesh", "उत्तराखंड": "Uttarakhand",
    "पश्चिम बंगाल": "West Bengal", "दिल्ली": "Delhi",
    "जम्मू और कश्मीर": "Jammu & Kashmir", "लद्दाख": "Ladakh",
}

# ─── District Aliases ──────────────────────────────────────────────────────

DISTRICT_ALIASES: Dict[str, str] = {
    "bangalore": "Bengaluru", "bengaluru": "Bengaluru", "bangalore urban": "Bengaluru",
    "bangalore rural": "Bengaluru Rural",
    "calcutta": "Kolkata", "madras": "Chennai", "bombay": "Mumbai",
    "poona": "Pune", "lucknow": "Lucknow", "jaipur": "Jaipur",
    "chandigarh": "Chandigarh", "bhopal": "Bhopal",
    "hyderabad": "Hyderabad", "ahmedabad": "Ahmedabad",
    "pune": "Pune", "nagpur": "Nagpur",
    "coimbatore": "Coimbatore", "madurai": "Madurai",
    "Patna": "Patna", "patna": "Patna",
    "varanasi": "Varanasi", "kanpur": "Kanpur",
    "agra": "Agra", "meerut": "Meerut",
    "dehradun": "Dehradun", "shimla": "Shimla",
    "gangtok": "Gangtok", "shillong": "Shillong",
    "imphal": "Imphal", "aizawl": "Aizawl",
    "kohima": "Kohima", "itanagar": "Itanagar",
    "agartala": "Agartala", "panaji": "Panaji",
    "gandhinagar": "Gandhinagar", "ranchi": "Ranchi",
    "raipur": "Raipur", "bhubaneswar": "Bhubaneswar",
    "dispur": "Dispur", "guwahati": "Guwahati",
}

# ─── Query Pattern Aliases (common city-to-district mappings) ───────────────

CITY_TO_DISTRICT_STATE: Dict[str, Tuple[str, str]] = {
    "jaipur": ("Jaipur", "Rajasthan"),
    "udaipur": ("Udaipur", "Rajasthan"),
    "jodhpur": ("Jodhpur", "Rajasthan"),
    "kota": ("Kota", "Rajasthan"),
    "bikaner": ("Bikaner", "Rajasthan"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
    "varanasi": ("Varanasi", "Uttar Pradesh"),
    "kanpur": ("Kanpur", "Uttar Pradesh"),
    "agra": ("Agra", "Uttar Pradesh"),
    "meerut": ("Meerut", "Uttar Pradesh"),
    "noida": ("Gautam Buddh Nagar", "Uttar Pradesh"),
    "ghaziabad": ("Ghaziabad", "Uttar Pradesh"),
    "patna": ("Patna", "Bihar"),
    "gaya": ("Gaya", "Bihar"),
    "muzaffarpur": ("Muzaffarpur", "Bihar"),
    "bangalore": ("Bengaluru Urban", "Karnataka"),
    "bengaluru": ("Bengaluru Urban", "Karnataka"),
    "mysore": ("Mysuru", "Karnataka"),
    "mangalore": ("Dakshina Kannada", "Karnataka"),
    "hubli": ("Dharwad", "Karnataka"),
    "belgaum": ("Belagavi", "Karnataka"),
    "hyderabad": ("Hyderabad", "Telangana"),
    "warangal": ("Warangal Urban", "Telangana"),
    "nizamabad": ("Nizamabad", "Telangana"),
    "chennai": ("Chennai", "Tamil Nadu"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
    "madurai": ("Madurai", "Tamil Nadu"),
    "trichy": ("Tiruchirappalli", "Tamil Nadu"),
    "salem": ("Salem", "Tamil Nadu"),
    "erode": ("Erode", "Tamil Nadu"),
    "mumbai": ("Mumbai", "Maharashtra"),
    "pune": ("Pune", "Maharashtra"),
    "nagpur": ("Nagpur", "Maharashtra"),
    "nashik": ("Nashik", "Maharashtra"),
    "aurangabad": ("Chhatrapati Sambhajinagar", "Maharashtra"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "surat": ("Surat", "Gujarat"),
    "rajkot": ("Rajkot", "Gujarat"),
    "vadodara": ("Vadodara", "Gujarat"),
    "gandhinagar": ("Gandhinagar", "Gujarat"),
    "bhopal": ("Bhopal", "Madhya Pradesh"),
    "indore": ("Indore", "Madhya Pradesh"),
    "jabalpur": ("Jabalpur", "Madhya Pradesh"),
    "gwalior": ("Gwalior", "Madhya Pradesh"),
    "raipur": ("Raipur", "Chhattisgarh"),
    "ranchi": ("Ranchi", "Jharkhand"),
    "jamshedpur": ("East Singhbhum", "Jharkhand"),
    "dhanbad": ("Dhanbad", "Jharkhand"),
    "bhubaneswar": ("Khordha", "Odisha"),
    "cuttack": ("Cuttack", "Odisha"),
    "kolkata": ("Kolkata", "West Bengal"),
    "howrah": ("Howrah", "West Bengal"),
    "durgapur": ("Paschim Bardhaman", "West Bengal"),
    "siliguri": ("Darjeeling", "West Bengal"),
    "dehradun": ("Dehradun", "Uttarakhand"),
    "haridwar": ("Haridwar", "Uttarakhand"),
    "nainital": ("Nainital", "Uttarakhand"),
    "shimla": ("Shimla", "Himachal Pradesh"),
    "manali": ("Kullu", "Himachal Pradesh"),
    "chandigarh": ("Chandigarh", "Chandigarh"),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala"),
    "kochi": ("Ernakulam", "Kerala"),
    "kozhikode": ("Kozhikode", "Kerala"),
    "gangtok": ("East Sikkim", "Sikkim"),
    "shillong": ("East Khasi Hills", "Meghalaya"),
    "imphal": ("Imphal West", "Manipur"),
    "aizawl": ("Aizawl", "Mizoram"),
    "kohima": ("Kohima", "Nagaland"),
    "itanagar": ("Papum Pare", "Arunachal Pradesh"),
    "agartala": ("West Tripura", "Tripura"),
    "panaji": ("North Goa", "Goa"),
    "dispur": ("Kamrup Metropolitan", "Assam"),
    "guwahati": ("Kamrup Metropolitan", "Assam"),
}

# ─── Known Blocks (common ones from official data) ──────────────────────────

KNOWN_BLOCKS: Dict[str, Tuple[str, str]] = {
    "chomu": ("Chomu", "Jaipur", "Rajasthan"),
    "phaalera": ("Phaalera", "Jaipur", "Rajasthan"),
    "koil": ("Koil", "Alwar", "Rajasthan"),
    "kishangarh": ("Kishangarh", "Ajmer", "Rajasthan"),
    "basni": ("Basni", "Jodhpur", "Rajasthan"),
    "singhala": ("Singhala", "Bhiwani", "Haryana"),
    "tohana": ("Tohana", "Fatehabad", "Haryana"),
    "narwana": ("Narwana", "Jind", "Haryana"),
    "karnal": ("Karnal", "Karnal", "Haryana"),
    "panipat": ("Panipat", "Panipat", "Haryana"),
    "sonipat": ("Sonipat", "Sonipat", "Haryana"),
    "rohtak": ("Rohtak", "Rohtak", "Haryana"),
    "hisar": ("Hisar", "Hisar", "Haryana"),
    "sirsa": ("Sirsa", "Sirsa", "Haryana"),
    "fatehabad": ("Fatehabad", "Fatehabad", "Haryana"),
    "amritsar": ("Amritsar", "Amritsar", "Punjab"),
    "ludhiana": ("Ludhiana", "Ludhiana", "Punjab"),
    "jalandhar": ("Jalandhar", "Jalandhar", "Punjab"),
    "patiala": ("Patiala", "Patiala", "Punjab"),
    "bathinda": ("Bathinda", "Bathinda", "Punjab"),
    "moga": ("Moga", "Moga", "Punjab"),
    "sangrur": ("Sangrur", "Sangrur", "Punjab"),
    "hoshiarpur": ("Hoshiarpur", "Hoshiarpur", "Punjab"),
    "gurdaspur": ("Gurdaspur", "Gurdaspur", "Punjab"),
    "kapurthala": ("Kapurthala", "Kapurthala", "Punjab"),
    "faridabad": ("Faridabad", "Faridabad", "Haryana"),
    "gurgaon": ("Gurugram", "Gurugram", "Haryana"),
    "gurugram": ("Gurugram", "Gurugram", "Haryana"),
    "meerut": ("Meerut", "Meerut", "Uttar Pradesh"),
    "muzaffarnagar": ("Muzaffarnagar", "Muzaffarnagar", "Uttar Pradesh"),
    "saharanpur": ("Saharanpur", "Saharanpur", "Uttar Pradesh"),
    "bareilly": ("Bareilly", "Bareilly", "Uttar Pradesh"),
    "lucknow": ("Lucknow", "Lucknow", "Uttar Pradesh"),
    "kanpur": ("Kanpur Nagar", "Kanpur Nagar", "Uttar Pradesh"),
    "agra": ("Agra", "Agra", "Uttar Pradesh"),
    "aligarh": ("Aligarh", "Aligarh", "Uttar Pradesh"),
    "gorakhpur": ("Gorakhpur", "Gorakhpur", "Uttar Pradesh"),
    "varanasi": ("Varanasi", "Varanasi", "Uttar Pradesh"),
    "allahabad": ("Prayagraj", "Prayagraj", "Uttar Pradesh"),
    "prayagraj": ("Prayagraj", "Prayagraj", "Uttar Pradesh"),
    "noida": ("Dadri", "Gautam Buddh Nagar", "Uttar Pradesh"),
    "ghaziabad": ("Ghaziabad", "Ghaziabad", "Uttar Pradesh"),
    "bengaluru": ("Bengaluru North", "Bengaluru Urban", "Karnataka"),
    "mysuru": ("Mysuru", "Mysuru", "Karnataka"),
    "hubballi": ("Hubballi", "Dharwad", "Karnataka"),
    "belagavi": ("Belagavi", "Belagavi", "Karnataka"),
    "mangaluru": ("Mangaluru", "Dakshina Kannada", "Karnataka"),
    "ballari": ("Bellary", "Ballari", "Karnataka"),
    "raichur": ("Raichur", "Raichur", "Karnataka"),
    "koppal": ("Koppal", "Koppal", "Karnataka"),
    "bagalkot": ("Bagalkot", "Bagalkot", "Karnataka"),
    "vijayapura": ("Vijayapura", "Vijayapura", "Karnataka"),
    "kalaburagi": ("Kalaburagi", "Kalaburagi", "Karnataka"),
    "chamarajanagar": ("Chamarajanagar", "Chamarajanagar", "Karnataka"),
    "tumakuru": ("Tumakuru", "Tumakuru", "Karnataka"),
    "hassan": ("Hassan", "Hassan", "Karnataka"),
    "mandya": ("Mandya", "Mandya", "Karnataka"),
    "shimoga": ("Shivamogga", "Shivamogga", "Karnataka"),
    "davangere": ("Davangere", "Davangere", "Karnataka"),
    "chitradurga": ("Chitradurga", "Chitradurga", "Karnataka"),
    "chikkaballapura": ("Chikkaballapura", "Chikkaballapura", "Karnataka"),
    "kolar": ("Kolar", "Kolar", "Karnataka"),
    "udupi": ("Udupi", "Udupi", "Karnataka"),
    "kodagu": ("Kodagu", "Kodagu", "Karnataka"),
    "dakshina kannada": ("Mangaluru", "Dakshina Kannada", "Karnataka"),
    "north delhi": ("North Delhi", "North Delhi", "Delhi"),
    "south delhi": ("South Delhi", "South Delhi", "Delhi"),
    "east delhi": ("East Delhi", "East Delhi", "Delhi"),
    "west delhi": ("West Delhi", "West Delhi", "Delhi"),
    "central delhi": ("Central Delhi", "Central Delhi", "Delhi"),
    "new delhi": ("New Delhi", "New Delhi", "Delhi"),
    "north east delhi": ("North East Delhi", "North East Delhi", "Delhi"),
    "north west delhi": ("North West Delhi", "North West Delhi", "Delhi"),
    "shaheed bhagat singh nagar": ("Shahdara", "East Delhi", "Delhi"),
    "south east delhi": ("South East Delhi", "South East Delhi", "Delhi"),
    "south west delhi": ("South West Delhi", "South West Delhi", "Delhi"),
}


# ─── Resolution Functions ──────────────────────────────────────────────────

def resolve_state(text: str) -> Optional[str]:
    """Resolve any state reference to canonical name."""
    if not text:
        return None
    t = text.strip().lower()

    # Direct canonical match
    if t in STATE_CANONICAL:
        return STATE_CANONICAL[t]

    # Abbreviation
    if t in STATE_ABBREVIATIONS:
        return STATE_ABBREVIATIONS[t]

    # Hindi
    if text.strip() in STATE_HINDI:
        return STATE_HINDI[text.strip()]

    # Partial match
    for key, canonical in STATE_CANONICAL.items():
        if t in key or key in t:
            return canonical

    return None


def resolve_district(text: str, state: Optional[str] = None) -> Optional[str]:
    """Resolve district name to canonical form."""
    if not text:
        return None
    t = text.strip().lower()

    # Check city-to-district mapping
    if t in CITY_TO_DISTRICT_STATE:
        district, _ = CITY_TO_DISTRICT_STATE[t]
        return district

    # Check district aliases
    if t in DISTRICT_ALIASES:
        return DISTRICT_ALIASES[t]

    # Title case as fallback
    return text.strip().title()


def resolve_location(query: str) -> Dict[str, Optional[str]]:
    """Extract and resolve all geographic entities from a query."""
    result: Dict[str, Optional[str]] = {"state": None, "district": None, "block": None}
    lower_q = query.lower()

    # Check city-to-district-state mappings first
    for city, (district, state) in CITY_TO_DISTRICT_STATE.items():
        if city in lower_q:
            result["district"] = district
            result["state"] = state
            break

    # Check state
    for key, canonical in STATE_CANONICAL.items():
        if key in lower_q:
            result["state"] = canonical
            break

    # Check abbreviations (word boundary)
    for abbr, canonical in STATE_ABBREVIATIONS.items():
        if f" {abbr} " in f" {lower_q} " or lower_q.startswith(f"{abbr} ") or lower_q.endswith(f" {abbr}"):
            if not result["state"]:
                result["state"] = canonical
            break

    # Check Hindi state names
    for hindi, canonical in STATE_HINDI.items():
        if hindi in query:
            result["state"] = canonical
            break

    # Check blocks
    for block_key, (block_name, district, state) in KNOWN_BLOCKS.items():
        if block_key in lower_q:
            result["block"] = block_name
            if not result["district"]:
                result["district"] = district
            if not result["state"]:
                result["state"] = state
            break

    return result


def get_all_states() -> List[str]:
    """Return list of all canonical state/UT names."""
    seen = set()
    states = []
    for canonical in STATE_CANONICAL.values():
        if canonical not in seen:
            seen.add(canonical)
            states.append(canonical)
    return sorted(states)
