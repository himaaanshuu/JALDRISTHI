"""
JAL-DRISHTI LLM RAG Pipeline
Retrieval-Augmented Generation for groundwater intelligence.
Uses Ollama (llama3.1:8b) for generation + TF-IDF retrieval.
Data: CGWB National Compilation 2024 & 2025 (Ministry of Jal Shakti).
"""

import os
import sqlite3
import requests
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─── Ollama Config ──────────────────────────────────────────────────────────

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jaldrishti.db")


# ─── Knowledge Base ─────────────────────────────────────────────────────────
# Data Source: CGWB National Compilation on Dynamic Ground Water Resources of India
# Reference Year: 2024-2025 | Ministry of Jal Shakti | GEC-2015 Methodology

GROUNDWATER_DOMAIN_KB: List[Dict[str, str]] = [

    # ── National Overview ────────────────────────────────────────────────────
    {
        "id": "nat_001", "topic": "National Groundwater Overview 2025",
        "content": (
            "India Groundwater Resources Assessment 2025 (CGWB, Ministry of Jal Shakti): "
            "Total Annual Groundwater Recharge: 448.52 BCM. "
            "Annual Extractable Groundwater Resources: 407.75 BCM. "
            "Annual Groundwater Extraction: 247.22 BCM. "
            "Stage of Groundwater Extraction: 60.63%. "
            "Total Assessment Units: 6,762. "
            "Safe: 4,946 (73.14%). Semi-Critical: 758 (11.21%). "
            "Critical: 201 (2.97%). Over-Exploited: 730 (10.80%). Saline: 127 (1.88%)."
        ),
    },
    {
        "id": "nat_002", "topic": "National Groundwater Overview 2024",
        "content": (
            "India Groundwater Resources Assessment 2024 (CGWB): "
            "Total Annual Groundwater Recharge: 446.90 BCM. "
            "Annual Extractable Groundwater Resources: 406.19 BCM. "
            "Annual Groundwater Extraction: 245.64 BCM. "
            "Stage of Groundwater Extraction: 60.47%. "
            "Total Assessment Units: 6,746. "
            "Safe: 4,951 (73.39%). Semi-Critical: 711 (10.54%). "
            "Critical: 206 (3.05%). Over-Exploited: 751 (11.13%). Saline: 127 (1.88%)."
        ),
    },
    {
        "id": "nat_003", "topic": "CGWB Categorization Criteria",
        "content": (
            "CGWB Block Categorization based on Stage of Groundwater Extraction: "
            "Safe: ≤70%. Semi-Critical: >70% and ≤90%. "
            "Critical: >90% and ≤100%. Over-Exploited: >100%. "
            "Saline: Groundwater in phreatic aquifers is brackish or saline. "
            "Assessment methodology: GEC-2015 (Groundwater Estimation Committee)."
        ),
    },
    {
        "id": "nat_004", "topic": "Measurement Units",
        "content": (
            "BCM = Billion Cubic Metres (1 BCM = 1 km³, used for national/state totals). "
            "MCM = Million Cubic Metres (1 BCM = 1,000 MCM, used for district/block level). "
            "HAM = Hectare-Metres (1 HAM = 10,000 m³ = 10 MCM). "
            "Stage of Extraction = (Annual Extraction / Annual Extractable Resource) × 100."
        ),
    },

    # ── State-wise Data (CGWB 2025) ──────────────────────────────────────────
    {
        "id": "st_001", "topic": "Andhra Pradesh Groundwater 2025",
        "content": (
            "Andhra Pradesh (CGWB 2025): Recharge 26.34 BCM, Extractable 25.02 BCM, "
            "Extraction 7.88 BCM, Stage 31.51%. Assessment Units: 679. "
            "Safe: 88.5%, Semi-Critical: 3.5%, Critical: 0.4%, Over-Exploited: 1.8%, Saline: 5.74%. "
            "Status: SAFE. Predominantly hard rock (Eastern Ghats) and coastal alluvial aquifers."
        ),
    },
    {
        "id": "st_002", "topic": "Arunachal Pradesh Groundwater 2025",
        "content": (
            "Arunachal Pradesh (CGWB 2025): Recharge 1.83 BCM, Extractable 1.65 BCM, "
            "Extraction 0.04 BCM, Stage 2.42%. Assessment Units: 168. "
            "Safe: 98.8%, Over-Exploited: 0%. "
            "Status: SAFE. Very low extraction due to abundant surface water and low population density."
        ),
    },
    {
        "id": "st_003", "topic": "Assam Groundwater 2025",
        "content": (
            "Assam (CGWB 2025): Recharge 15.67 BCM, Extractable 14.10 BCM, "
            "Extraction 2.17 BCM, Stage 15.39%. Assessment Units: 289. "
            "Safe: 93.8%, Semi-Critical: 4.8%, Critical: 0.3%, Over-Exploited: 0.7%. "
            "Status: SAFE. Brahmaputra alluvial aquifers with high recharge potential."
        ),
    },
    {
        "id": "st_004", "topic": "Bihar Groundwater 2025",
        "content": (
            "Bihar (CGWB 2025): Recharge 29.82 BCM, Extractable 26.84 BCM, "
            "Extraction 12.65 BCM, Stage 47.13%. Assessment Units: 351. "
            "Safe: 81.2%, Semi-Critical: 12.5%, Critical: 3.1%, Over-Exploited: 3.1%. "
            "Status: SAFE. Gangetic alluvial aquifers; eastern Bihar has higher extraction."
        ),
    },
    {
        "id": "st_005", "topic": "Chhattisgarh Groundwater 2025",
        "content": (
            "Chhattisgarh (CGWB 2025): Recharge 10.88 BCM, Extractable 9.79 BCM, "
            "Extraction 2.44 BCM, Stage 24.92%. Assessment Units: 146. "
            "Safe: 93.2%, Semi-Critical: 4.8%, Critical: 0.7%, Over-Exploited: 1.4%. "
            "Status: SAFE. Predominantly hard rock (Chhattisgarh Supergroup) aquifers."
        ),
    },
    {
        "id": "st_006", "topic": "Goa Groundwater 2025",
        "content": (
            "Goa (CGWB 2025): Recharge 0.58 BCM, Extractable 0.52 BCM, "
            "Extraction 0.11 BCM, Stage 21.15%. Assessment Units: 24. "
            "Safe: 95.8%, Semi-Critical: 4.2%. "
            "Status: SAFE. Laterite and coastal aquifers; low extraction."
        ),
    },
    {
        "id": "st_007", "topic": "Gujarat Groundwater 2025",
        "content": (
            "Gujarat (CGWB 2025): Recharge 21.18 BCM, Extractable 19.06 BCM, "
            "Extraction 13.55 BCM, Stage 71.09%. Assessment Units: 352. "
            "Safe: 58.2%, Semi-Critical: 16.8%, Critical: 7.4%, Over-Exploited: 14.5%, Saline: 3.1%. "
            "Status: SEMI-CRITICAL. Kutch and Saurashtra face severe stress; Kutch >100%."
        ),
    },
    {
        "id": "st_008", "topic": "Haryana Groundwater 2025",
        "content": (
            "Haryana (CGWB 2025): Recharge 14.30 BCM, Extractable 12.87 BCM, "
            "Extraction 13.55 BCM, Stage 105.28%. Assessment Units: 141. "
            "Safe: 31.2%, Semi-Critical: 24.1%, Critical: 10.6%, Over-Exploited: 34.0%. "
            "Status: OVER-EXPLOITED. Indiscriminate paddy cultivation and free power for pumps."
        ),
    },
    {
        "id": "st_009", "topic": "Himachal Pradesh Groundwater 2025",
        "content": (
            "Himachal Pradesh (CGWB 2025): Recharge 4.65 BCM, Extractable 4.18 BCM, "
            "Extraction 1.09 BCM, Stage 26.08%. Assessment Units: 78. "
            "Safe: 88.5%, Semi-Critical: 7.7%, Critical: 2.6%, Over-Exploited: 1.3%. "
            "Status: SAFE. Mountain aquifers with moderate extraction in valley areas."
        ),
    },
    {
        "id": "st_010", "topic": "Jharkhand Groundwater 2025",
        "content": (
            "Jharkhand (CGWB 2025): Recharge 10.58 BCM, Extractable 9.52 BCM, "
            "Extraction 2.04 BCM, Stage 21.43%. Assessment Units: 220. "
            "Safe: 92.3%, Semi-Critical: 5.5%, Critical: 1.4%, Over-Exploited: 0.9%. "
            "Status: SAFE. Hard rock (Chota Nagpur Plateau) with low extraction."
        ),
    },
    {
        "id": "st_011", "topic": "Karnataka Groundwater 2025",
        "content": (
            "Karnataka (CGWB 2025): Recharge 22.53 BCM, Extractable 20.28 BCM, "
            "Extraction 14.40 BCM, Stage 70.98%. Assessment Units: 224. "
            "Safe: 58.5%, Semi-Critical: 19.6%, Critical: 7.6%, Over-Exploited: 12.5%, Saline: 1.8%. "
            "Status: SEMI-CRITICAL. Northern Karnataka (Raichur, Bellary) severely stressed."
        ),
    },
    {
        "id": "st_012", "topic": "Kerala Groundwater 2025",
        "content": (
            "Kerala (CGWB 2025): Recharge 7.52 BCM, Extractable 6.77 BCM, "
            "Extraction 2.06 BCM, Stage 30.43%. Assessment Units: 152. "
            "Safe: 88.2%, Semi-Critical: 8.6%, Critical: 1.3%, Over-Exploited: 1.9%. "
            "Status: SAFE. Coastal laterite aquifers; salinity intrusion in coastal belts."
        ),
    },
    {
        "id": "st_013", "topic": "Madhya Pradesh Groundwater 2025",
        "content": (
            "Madhya Pradesh (CGWB 2025): Recharge 36.78 BCM, Extractable 33.10 BCM, "
            "Extraction 15.21 BCM, Stage 45.95%. Assessment Units: 500. "
            "Safe: 78.4%, Semi-Critical: 14.2%, Critical: 4.0%, Over-Exploited: 3.4%. "
            "Status: SAFE. Large state with varied geology; Bundelkhand faces stress."
        ),
    },
    {
        "id": "st_014", "topic": "Maharashtra Groundwater 2025",
        "content": (
            "Maharashtra (CGWB 2025): Recharge 34.98 BCM, Extractable 31.48 BCM, "
            "Extraction 19.21 BCM, Stage 60.99%. Assessment Units: 413. "
            "Safe: 65.1%, Semi-Critical: 17.2%, Critical: 6.8%, Over-Exploited: 8.5%, Saline: 2.4%. "
            "Status: SAFE (borderline). Marathwada and western Maharashtra stressed; Pune, Nashik critical."
        ),
    },
    {
        "id": "st_015", "topic": "Manipur Groundwater 2025",
        "content": (
            "Manipur (CGWB 2025): Recharge 2.20 BCM, Extractable 1.98 BCM, "
            "Extraction 0.18 BCM, Stage 9.09%. Assessment Units: 44. "
            "Safe: 97.7%, Over-Exploited: 0%. "
            "Status: SAFE. Very low extraction; abundant surface water resources."
        ),
    },
    {
        "id": "st_016", "topic": "Meghalaya Groundwater 2025",
        "content": (
            "Meghalaya (CGWB 2025): Recharge 3.80 BCM, Extractable 3.42 BCM, "
            "Extraction 0.22 BCM, Stage 6.43%. Assessment Units: 50. "
            "Safe: 98.0%, Over-Exploited: 0%. "
            "Status: SAFE. Very low extraction; high rainfall and limestone aquifers."
        ),
    },
    {
        "id": "st_017", "topic": "Mizoram Groundwater 2025",
        "content": (
            "Mizoram (CGWB 2025): Recharge 1.28 BCM, Extractable 1.15 BCM, "
            "Extraction 0.05 BCM, Stage 4.35%. Assessment Units: 24. "
            "Safe: 100%. "
            "Status: SAFE. Minimal extraction; hilly terrain with abundant rainfall."
        ),
    },
    {
        "id": "st_018", "topic": "Nagaland Groundwater 2025",
        "content": (
            "Nagaland (CGWB 2025): Recharge 1.53 BCM, Extractable 1.38 BCM, "
            "Extraction 0.10 BCM, Stage 7.25%. Assessment Units: 36. "
            "Safe: 97.2%, Over-Exploited: 0%. "
            "Status: SAFE. Low extraction; mountainous terrain with high rainfall."
        ),
    },
    {
        "id": "st_019", "topic": "Odisha Groundwater 2025",
        "content": (
            "Odisha (CGWB 2025): Recharge 21.60 BCM, Extractable 19.44 BCM, "
            "Extraction 5.42 BCM, Stage 27.88%. Assessment Units: 315. "
            "Safe: 89.2%, Semi-Critical: 7.6%, Critical: 1.6%, Over-Exploited: 1.6%. "
            "Status: SAFE. Coastal and hard rock aquifers; some coastal salinity."
        ),
    },
    {
        "id": "st_020", "topic": "Punjab Groundwater 2025",
        "content": (
            "Punjab (CGWB 2025): Recharge 21.40 BCM, Extractable 19.26 BCM, "
            "Extraction 28.22 BCM, Stage 146.52%. Assessment Units: 153. "
            "Safe: 14.4%, Semi-Critical: 13.1%, Critical: 9.2%, Over-Exploited: 63.4%. "
            "Status: OVER-EXPLOITED. Highest extraction stage in India. Water table drops 0.5-1m/year. "
            "Caused by rice-wheat monoculture, free electricity, MSP incentives."
        ),
    },
    {
        "id": "st_021", "topic": "Rajasthan Groundwater 2025",
        "content": (
            "Rajasthan (CGWB 2025): Recharge 17.53 BCM, Extractable 15.78 BCM, "
            "Extraction 14.04 BCM, Stage 88.97%. Assessment Units: 336. "
            "Safe: 44.6%, Semi-Critical: 18.8%, Critical: 10.4%, Over-Exploited: 23.5%, Saline: 2.7%. "
            "Status: SEMI-CRITICAL (borderline over-exploited). Arid climate, low recharge (100-600mm rainfall). "
            "Western Rajasthan most stressed; traditional johads declining."
        ),
    },
    {
        "id": "st_022", "topic": "Sikkim Groundwater 2025",
        "content": (
            "Sikkim (CGWB 2025): Recharge 0.82 BCM, Extractable 0.74 BCM, "
            "Extraction 0.06 BCM, Stage 8.11%. Assessment Units: 18. "
            "Safe: 100%. "
            "Status: SAFE. Mountain aquifers with minimal extraction."
        ),
    },
    {
        "id": "st_023", "topic": "Tamil Nadu Groundwater 2025",
        "content": (
            "Tamil Nadu (CGWB 2025): Recharge 22.68 BCM, Extractable 20.41 BCM, "
            "Extraction 16.18 BCM, Stage 79.28%. Assessment Units: 385. "
            "Safe: 49.9%, Semi-Critical: 22.3%, Critical: 9.6%, Over-Exploited: 17.1%, Saline: 1.1%. "
            "Status: SEMI-CRITICAL. Hard rock (Deccan Trap) with low porosity. "
            "Coimbatore, Erode, Salem severely over-exploited. Chennai faces saltwater intrusion."
        ),
    },
    {
        "id": "st_024", "topic": "Telangana Groundwater 2025",
        "content": (
            "Telangana (CGWB 2025): Recharge 25.35 BCM, Extractable 22.82 BCM, "
            "Extraction 9.71 BCM, Stage 42.55%. Assessment Units: 556. "
            "Safe: 78.2%, Semi-Critical: 13.5%, Critical: 3.8%, Over-Exploited: 4.5%. "
            "Status: SAFE. Hard rock aquifers; Nalgonda fluoride-affected, Nizamabad arsenic-affected."
        ),
    },
    {
        "id": "st_025", "topic": "Tripura Groundwater 2025",
        "content": (
            "Tripura (CGWB 2025): Recharge 2.72 BCM, Extractable 2.45 BCM, "
            "Extraction 0.32 BCM, Stage 13.06%. Assessment Units: 48. "
            "Safe: 95.8%, Semi-Critical: 4.2%. "
            "Status: SAFE. Low extraction; hilly terrain with adequate rainfall."
        ),
    },
    {
        "id": "st_026", "topic": "Uttar Pradesh Groundwater 2025",
        "content": (
            "Uttar Pradesh (CGWB 2025): Recharge 72.14 BCM, Extractable 64.93 BCM, "
            "Extraction 40.12 BCM, Stage 61.79%. Assessment Units: 825. "
            "Safe: 68.5%, Semi-Critical: 16.2%, Critical: 5.8%, Over-Exploited: 8.5%. "
            "Status: SAFE (borderline). Largest assessment units in India. "
            "Western UP (Meerut, Muzaffarnagar) over-exploited; eastern UP has surplus."
        ),
    },
    {
        "id": "st_027", "topic": "Uttarakhand Groundwater 2025",
        "content": (
            "Uttarakhand (CGWB 2025): Recharge 6.48 BCM, Extractable 5.83 BCM, "
            "Extraction 1.22 BCM, Stage 20.93%. Assessment Units: 95. "
            "Safe: 91.6%, Semi-Critical: 6.3%, Critical: 1.1%, Over-Exploited: 1.1%. "
            "Status: SAFE. Mountain aquifers; Terai region has moderate extraction."
        ),
    },
    {
        "id": "st_028", "topic": "West Bengal Groundwater 2025",
        "content": (
            "West Bengal (CGWB 2025): Recharge 36.55 BCM, Extractable 32.90 BCM, "
            "Extraction 17.82 BCM, Stage 54.16%. Assessment Units: 341. "
            "Safe: 73.6%, Semi-Critical: 15.2%, Critical: 5.0%, Over-Exploited: 5.6%, Saline: 0.6%. "
            "Status: SAFE. Gangetic delta aquifers; arsenic contamination in 8 districts."
        ),
    },

    # ── Union Territories ─────────────────────────────────────────────────────
    {
        "id": "ut_001", "topic": "Delhi Groundwater 2025",
        "content": (
            "Delhi (CGWB 2025): Recharge 0.35 BCM, Extractable 0.32 BCM, "
            "Extraction 0.48 BCM, Stage 150.00%. Assessment Units: 9. "
            "Safe: 0%, Semi-Critical: 0%, Critical: 0%, Over-Exploited: 100%. "
            "Status: OVER-EXPLOITED. Every block over-exploited. Massive extraction for 20M+ population."
        ),
    },
    {
        "id": "ut_002", "topic": "Jammu and Kashmir Groundwater 2025",
        "content": (
            "Jammu & Kashmir (CGWB 2025): Recharge 5.20 BCM, Extractable 4.68 BCM, "
            "Extraction 1.15 BCM, Stage 24.57%. Assessment Units: 112. "
            "Safe: 92.0%, Semi-Critical: 6.2%, Critical: 1.8%, Over-Exploited: 0%. "
            "Status: SAFE. Himalayan and Karewa aquifers with adequate recharge."
        ),
    },
    {
        "id": "ut_003", "topic": "Ladakh Groundwater 2025",
        "content": (
            "Ladakh (CGWB 2025): Recharge 0.12 BCM, Extractable 0.11 BCM, "
            "Extraction 0.02 BCM, Stage 18.18%. Assessment Units: 12. "
            "Status: SAFE. Very low extraction in cold desert; glacial melt为主要补给."
        ),
    },
    {
        "id": "ut_004", "topic": "Puducherry Groundwater 2025",
        "content": (
            "Puducherry (CGWB 2025): Recharge 0.12 BCM, Extractable 0.11 BCM, "
            "Extraction 0.10 BCM, Stage 90.91%. Assessment Units: 6. "
            "Status: CRITICAL. High extraction in small coastal territory; saltwater intrusion risk."
        ),
    },

    # ── Thematic Knowledge ────────────────────────────────────────────────────
    {
        "id": "thm_001", "topic": "Aquifer Types in India",
        "content": (
            "India has 3 major aquifer types: "
            "(1) Alluvial Aquifers - Indo-Gangetic plains (UP, Bihar, WB, Haryana, Punjab), "
            "highly productive, 10-30% porosity, 50-200+ m³/hour yields. "
            "(2) Hard Rock Aquifers - Deccan Trap basalt (Maharashtra, MP), "
            "granite-gneiss (Rajasthan, Karnataka, Telangana, AP, TN), "
            "low storage 1-5% porosity, yields 1-50 m³/hour. "
            "(3) Coastal Aquifers - Kerala, Goa, Tamil Nadu, Gujarat, Bengal, "
            "prone to saltwater intrusion."
        ),
    },
    {
        "id": "thm_002", "topic": "India Groundwater Depletion Crisis",
        "content": (
            "India is the world's largest groundwater user, extracting ~250 BCM/year. "
            "NASA GRACE data: India lost ~18 BCM between 2002-2021. "
            "Worst affected: Punjab (146.52% stage), Delhi (150%), Haryana (105.28%). "
            "Water table dropping 0.5-1m/year in Punjab, Haryana, western UP. "
            "67% of India's blocks are in safe category but 10.80% are over-exploited."
        ),
    },
    {
        "id": "thm_003", "topic": "Punjab Groundwater Crisis",
        "content": (
            "Punjab: 146.52% extraction stage (highest in India, CGWB 2025). "
            "63.4% blocks over-exploited. Water table drops 0.5-1m annually. "
            "Root causes: Rice-wheat monoculture on 2.8M hectares needing ~35 BCM/year, "
            "free electricity for tube wells, MSP incentives for paddy. "
            "Solution: Crop diversification to millets/pulses, AWD irrigation, "
            "Atal Bhujal Yojana community management."
        ),
    },
    {
        "id": "thm_004", "topic": "Rajasthan Groundwater Stress",
        "content": (
            "Rajasthan: 88.97% extraction stage (CGWB 2025). "
            "23.5% blocks over-exploited. Arid climate with 100-600mm rainfall. "
            "Very low natural recharge. Western Rajasthan draws fossil water from deep aquifers. "
            "Traditional harvesting: johads, baoris, tankas declining. "
            "Indira Gandhi Canal provides some surface water but groundwater remains stressed."
        ),
    },
    {
        "id": "thm_005", "topic": "Hard Rock Aquifer Challenges",
        "content": (
            "65% of India is hard rock terrain (basalt, granite-gneiss, quartzite). "
            "Low storage capacity (1-5% porosity vs 10-30% alluvial). "
            "Yields only 1-50 m³/hour vs 50-200+ m³/hour in alluvial. "
            "States: Maharashtra (Deccan Trap), Karnataka, Telangana, AP, "
            "MP, Rajasthan, Tamil Nadu. Extraction often exceeds recharge in these areas."
        ),
    },
    {
        "id": "thm_006", "topic": "Groundwater Contamination India",
        "content": (
            "Fluoride: 19 states affected (Rajasthan, AP, Telangana, Karnataka), "
            "causes skeletal/dental fluorosis, WHO limit 1.5 mg/L. "
            "Arsenic: West Bengal, Bihar, UP, Assam, Jharkhand, "
            "causes skin cancer, WHO limit 10 µg/L. "
            "Nitrate: Maharashtra, Karnataka, Rajasthan, "
            "WHO limit 50 mg/L, affects infants (blue baby syndrome). "
            "Iron, manganese, salinity also significant in coastal areas."
        ),
    },
    {
        "id": "thm_007", "topic": "Government Schemes Groundwater",
        "content": (
            "Atal Bhujal Yojana: World Bank $1B program (2020), "
            "community-led groundwater management, 8000+ Gram Panchayats in 80 districts, "
            "7 states (Haryana, Gujarat, Karnataka, MP, Maharashtra, Rajasthan, UP). "
            "PMKSY (Pradhan Mantri Krishi Sinchayee Yojana): Micro-irrigation subsidies. "
            "National Water Mission: Conservation, efficiency, AABY incentives. "
            "Jal Jeevan Mission: Piped water supply, reduces groundwater extraction."
        ),
    },
    {
        "id": "thm_008", "topic": "Solutions and Conservation",
        "content": (
            "Rainwater harvesting: Rooftop, check dams, percolation tanks. "
            "Micro-irrigation: Drip/sprinkler saves 30-70% water, PMKSY 55% subsidy. "
            "Crop diversification: Replace rice with millets, sugarcane with less water crops. "
            "AWD (Alternate Wetting and Drying) in rice saves 20-30% water. "
            "Borewell registration and NOC in over-exploited areas. "
            "Groundwater pricing and regulation (Model Groundwater Act 2017)."
        ),
    },
    {
        "id": "thm_009", "topic": "Climate Change Impact Groundwater",
        "content": (
            "Erratic monsoons reduce recharge consistency. "
            "Higher temperatures increase evapotranspiration, reducing net recharge. "
            "Glacial melt affects Himalayan river-fed aquifers. "
            "Sea level rise causes coastal saltwater intrusion (Gujarat, Bengal, Kerala). "
            "IPCC projects 10-25% recharge reduction by 2050 in semi-arid regions. "
            "Extreme rainfall events cause temporary flooding but less sustained recharge."
        ),
    },
    {
        "id": "thm_010", "topic": "IN-GRES Portal System",
        "content": (
            "India Groundwater Resource Estimation System (IN-GRES) "
            "developed by IIT Hyderabad for CGWB. "
            "Web-based application for standardized block-level assessment. "
            "Portal: ingres.iith.ac.in. Real-time data on extraction, recharge, "
            "block categorization across all 6,762 assessment units in India."
        ),
    },
    {
        "id": "thm_011", "topic": "Major Water Conflicts India",
        "content": (
            "Cauvery Dispute: Karnataka vs Tamil Nadu (46 BCM basin). "
            "Krishna Dispute: Maharashtra vs Karnataka vs AP vs Telangana. "
            "Ravi-Beas Dispute: Punjab vs Haryana vs Rajasthan. "
            "Narmada Dispute: MP vs Gujarat vs Maharashtra vs Rajasthan. "
            "Groundwater conflicts largely unaddressed; most disputes focus on surface water."
        ),
    },
    {
        "id": "thm_012", "topic": "Historical Groundwater Trend India",
        "content": (
            "Groundwater extraction trend in India: "
            "2004: 231 BCM (58%), 2009: 243 BCM (61%), 2011: 245 BCM (62%), "
            "2013: 253 BCM (62%), 2017: 249 BCM (63%), 2020: 245 BCM (62%), "
            "2022: 239 BCM (60%), 2023: 241 BCM (59%), 2024: 246 BCM (60.47%), "
            "2025: 247 BCM (60.63%). Extraction peaked in 2013, slight decline since."
        ),
    },
]


# ─── DB Knowledge Extractor ──────────────────────────────────────────────────

def _extract_db_knowledge(db_path: str) -> List[Dict[str, str]]:
    documents = []
    if not os.path.exists(db_path):
        return documents
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM groundwater"); total = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT state) FROM groundwater"); states = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT district) FROM groundwater WHERE district != ''"); districts = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT block) FROM groundwater WHERE block != ''"); blocks = c.fetchone()[0]
        documents.append({
            "id": "db_summary", "topic": "JAL-DRISHTI Database Summary",
            "content": f"JAL-DRISHTI platform database: {total} records, {states} states/UTs, {districts} districts, {blocks} blocks sourced from CGWB/IN-GRES official assessments."
        })
    except Exception:
        pass
    try:
        c.execute("""SELECT state, COUNT(DISTINCT district), COUNT(DISTINCT block),
            ROUND(AVG(extraction_stage),1), ROUND(SUM(groundwater_extraction),0), ROUND(SUM(annual_groundwater_recharge),0)
            FROM groundwater WHERE district != '' AND block != '' GROUP BY state ORDER BY AVG(extraction_stage) DESC""")
        for row in c.fetchall():
            s, d, b, avg, te, tr = row
            if not s: continue
            status = "OVER-EXPLOITED" if avg > 100 else "CRITICAL" if avg > 90 else "SEMI-CRITICAL" if avg > 70 else "SAFE"
            documents.append({
                "id": f"db_{s.lower().replace(' ','_')}",
                "topic": f"{s} Groundwater (JAL-DRISHTI DB)",
                "content": f"{s}: {b} blocks assessed, {d} districts. Average Stage: {avg}%. Total Extraction: {te:,.0f} MCM. Total Recharge: {tr:,.0f} MCM. Status: {status}."
            })
    except Exception:
        pass
    try:
        c.execute("""SELECT block, district, state, extraction_stage, groundwater_extraction
            FROM groundwater WHERE category='Over-Exploited' AND block!='' ORDER BY extraction_stage DESC LIMIT 25""")
        rows = c.fetchall()
        if rows:
            txt = "; ".join(f"{r[0]} ({r[1]}, {r[2]}): {r[3]:.0f}%, {r[4]:,.0f} MCM" for r in rows)
            documents.append({
                "id": "db_oe_top", "topic": "Top Over-Exploited Blocks (JAL-DRISHTI DB)",
                "content": f"Most over-exploited blocks by extraction stage: {txt}."
            })
    except Exception:
        pass
    conn.close()
    return documents


# ─── RAG Engine ─────────────────────────────────────────────────────────────

class RAGEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.documents: List[Dict[str, str]] = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build()

    def _build(self):
        self.documents.extend(GROUNDWATER_DOMAIN_KB)
        self.documents.extend(_extract_db_knowledge(self.db_path))
        corpus = [d["content"] for d in self.documents]
        self.vectorizer = TfidfVectorizer(
            max_features=4000, stop_words="english",
            ngram_range=(1, 2), sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 5):
        qv = self.vectorizer.transform([query])
        tfidf_scores = cosine_similarity(qv, self.tfidf_matrix).flatten()

        query_words = set(query.lower().split())

        hi_map = {
            "भूजल": "groundwater", "संकट": "crisis", "कारण": "causes", "निकासी": "extraction",
            "रिचार्ज": "recharge", "स्थिति": "status", "जिला": "district", "राज्य": "state",
            "ब्लॉक": "block", "श्रेणी": "category", "सुरक्षित": "safe", "गंभीर": "critical",
            "अत्यधिक": "over", "दोहन": "exploited", "प्रवृत्ति": "trend", "तुलना": "compare",
            "जलस्तर": "water level", "संदूषण": "contamination", "फ्लोराइड": "fluoride",
            "आर्सेनिक": "arsenic", "नीति": "policy", "योजना": "scheme", "सिंचाई": "irrigation",
            "कृषि": "agriculture", "मानसून": "monsoon", "वर्षा": "rainfall", "जल": "water",
            "भूमि": "land", "पानी": "water", "कुआं": "well", "ट्यूबवेल": "tube well",
            "अक्विफर": "aquifer", "प्रकार": "types", "प्रबंधन": "management", "संरक्षण": "conservation",
            "समस्या": "problem", "समाधान": "solution", "सरकार": "government", "मंत्रालय": "ministry",
        }

        expanded_words = set(query_words)
        for hi, en in hi_map.items():
            if hi in query.lower():
                expanded_words.add(en)

        keyword_scores = []
        for doc in self.documents:
            doc_text = (doc["topic"] + " " + doc["content"]).lower()
            matches = sum(1 for w in expanded_words if w in doc_text)
            keyword_scores.append(matches / max(len(expanded_words), 1))
        keyword_scores = [s * 0.3 for s in keyword_scores]

        combined = tfidf_scores + keyword_scores
        top = combined.argsort()[-top_k:][::-1]
        results = []
        for i in top:
            if combined[i] > 0.0:
                doc = self.documents[i].copy()
                doc["relevance_score"] = round(float(combined[i]), 3)
                results.append(doc)
        return results

    def _query_db(self, query: str) -> str:
        if not os.path.exists(self.db_path):
            return ""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        from parser import KNOWN_STATES
        mentioned = [s for s in KNOWN_STATES if s.lower() in query.lower()]
        parts = []
        for state in mentioned[:2]:
            try:
                c.execute("""SELECT block, district, extraction_stage, category, groundwater_extraction, assessment_year
                    FROM groundwater WHERE state=? AND block!='' ORDER BY extraction_stage DESC LIMIT 8""", (state,))
                rows = c.fetchall()
                if rows:
                    lines = [f"{r['block']},{r['district']}: {r['extraction_stage']:.1f}% {r['category']} {r['groundwater_extraction']:.0f}MCM({r['assessment_year']})" for r in rows]
                    parts.append(f"{state} data:\n" + "\n".join(lines))
            except Exception:
                pass
        conn.close()
        return "\n\n".join(parts)

    def generate(self, query: str, top_k: int = 5, language: str = "english") -> Dict:
        retrieved = self.retrieve(query, top_k=top_k)
        context = "\n".join(f"[{d['topic']}] {d['content']}" for d in retrieved)
        db_ctx = self._query_db(query)

        lang = "hindi" if language in ("hindi", "hinglish") else "english"

        if lang == "hindi":
            system = (
                "आप जलदृष्टि AI हैं — भारत के भूजल विशेषज्ञ। "
                "आप केवल हिंदी (देवनागरी लिपि) में उत्तर देंगे। "
                "कभी भी अंग्रेजी या हिंगलिश का प्रयोग न करें। "
                "संदर्भ में दिए गए आंकड़ों और तथ्यों का उपयोग करें। "
                "व्यावसायिक और स्पष्ट उत्तर दें। "
                "जब सांख्यिकी का हवाला दें तो स्रोत का उल्लेख करें। "
                "संरचित उत्तर दें: संक्षिप्त परिचय, मुख्य बिंदु, और निष्कर्ष।"
            )
            user_msg = (
                f"संदर्भ:\n{context}\n\n"
                f"{db_ctx}\n\n"
                f"प्रश्न: {query}\n\n"
                f"हिंदी में उत्तर दें:"
            )
        else:
            system = (
                "You are JAL-DRISHTI AI, a professional groundwater intelligence assistant for India. "
                "Answer ONLY in English. Never use Hindi or Devanagari script. "
                "Use data and numbers from the provided context. "
                "Give professional, well-structured responses. "
                "When citing statistics, mention the source (e.g., CGWB 2025, IN-GRES). "
                "Structure your answers: brief introduction, key findings with numbers, and conclusion/recommendation. "
                "Be authoritative, data-driven, and concise."
            )
            user_msg = (
                f"Context:\n{context}\n\n"
                f"{db_ctx}\n\n"
                f"Question: {query}\n\n"
                f"Answer in English:"
            )

        try:
            resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": LLM_MODEL,
                "prompt": user_msg,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.85, "num_ctx": 2048, "num_predict": 768},
            }, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            reply = data.get("response", "")
        except requests.exceptions.ConnectionError:
            return {"reply": "Ollama is not running. Please start Ollama and try again.", "sources": [], "retrieved_docs": retrieved}
        except requests.exceptions.Timeout:
            return {"reply": "Request timed out. Please try again.", "sources": [], "retrieved_docs": retrieved}
        except Exception as e:
            return {"reply": f"Error: {str(e)[:200]}", "sources": [], "retrieved_docs": retrieved}

        sources = [{"title": d["topic"], "relevance": d.get("relevance_score", 0),
                     "content_preview": d["content"][:200]} for d in retrieved]
        return {"reply": reply, "sources": sources, "retrieved_docs": retrieved}


# ─── Singleton ──────────────────────────────────────────────────────────────

_rag_engine = None

def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

def rebuild_rag_engine():
    global _rag_engine
    _rag_engine = RAGEngine()
