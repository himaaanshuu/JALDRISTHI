/**
 * State Mapping Utility for JALDRISTHI Groundwater Map
 * Maps between GeoJSON names, database names, and display names.
 */

export interface StateMapping {
  geoName: string;
  dbName: string;
  displayName: string;
  displayNameHi: string;
  lat: number;
  lng: number;
  type: 'State' | 'Union Territory';
}

export const STATE_MAPPINGS: StateMapping[] = [
  { geoName: 'Andaman and Nicobar', dbName: 'Andaman & Nicobar Islands', displayName: 'Andaman & Nicobar Islands', displayNameHi: 'अंडमान और निकोबार द्वीप समूह', lat: 11.74, lng: 92.72, type: 'Union Territory' },
  { geoName: 'Andhra Pradesh', dbName: 'Andhra Pradesh', displayName: 'Andhra Pradesh', displayNameHi: 'आंध्र प्रदेश', lat: 15.91, lng: 79.74, type: 'State' },
  { geoName: 'Arunachal Pradesh', dbName: 'Arunachal Pradesh', displayName: 'Arunachal Pradesh', displayNameHi: 'अरुणाचल प्रदेश', lat: 28.22, lng: 94.73, type: 'State' },
  { geoName: 'Assam', dbName: 'Assam', displayName: 'Assam', displayNameHi: 'असम', lat: 26.20, lng: 92.94, type: 'State' },
  { geoName: 'Bihar', dbName: 'Bihar', displayName: 'Bihar', displayNameHi: 'बिहार', lat: 25.10, lng: 85.31, type: 'State' },
  { geoName: 'Chandigarh', dbName: 'Chandigarh', displayName: 'Chandigarh', displayNameHi: 'चंडीगढ़', lat: 30.73, lng: 76.78, type: 'Union Territory' },
  { geoName: 'Chhattisgarh', dbName: 'Chhattisgarh', displayName: 'Chhattisgarh', displayNameHi: 'छत्तीसगढ़', lat: 21.27, lng: 81.87, type: 'State' },
  { geoName: 'Dadra and Nagar Haveli', dbName: 'Dadra & Nagar Haveli and Daman & Diu', displayName: 'Dadra & Nagar Haveli and Daman & Diu', displayNameHi: 'दादरा और नागर हवेली और दमन और दीव', lat: 20.18, lng: 73.02, type: 'Union Territory' },
  { geoName: 'Daman and Diu', dbName: 'Dadra & Nagar Haveli and Daman & Diu', displayName: 'Dadra & Nagar Haveli and Daman & Diu', displayNameHi: 'दादरा और नागर हवेली और दमन और दीव', lat: 20.18, lng: 73.02, type: 'Union Territory' },
  { geoName: 'Delhi', dbName: 'Delhi', displayName: 'Delhi', displayNameHi: 'दिल्ली', lat: 28.61, lng: 77.21, type: 'Union Territory' },
  { geoName: 'Goa', dbName: 'Goa', displayName: 'Goa', displayNameHi: 'गोवा', lat: 15.30, lng: 74.01, type: 'State' },
  { geoName: 'Gujarat', dbName: 'Gujarat', displayName: 'Gujarat', displayNameHi: 'गुजरात', lat: 22.26, lng: 71.19, type: 'State' },
  { geoName: 'Haryana', dbName: 'Haryana', displayName: 'Haryana', displayNameHi: 'हरियाणा', lat: 29.06, lng: 76.08, type: 'State' },
  { geoName: 'Himachal Pradesh', dbName: 'Himachal Pradesh', displayName: 'Himachal Pradesh', displayNameHi: 'हिमाचल प्रदेश', lat: 31.10, lng: 77.17, type: 'State' },
  { geoName: 'Jammu and Kashmir', dbName: 'Jammu & Kashmir', displayName: 'Jammu & Kashmir', displayNameHi: 'जम्मू और कश्मीर', lat: 33.78, lng: 76.58, type: 'Union Territory' },
  { geoName: 'Jharkhand', dbName: 'Jharkhand', displayName: 'Jharkhand', displayNameHi: 'झारखंड', lat: 23.61, lng: 85.28, type: 'State' },
  { geoName: 'Karnataka', dbName: 'Karnataka', displayName: 'Karnataka', displayNameHi: 'कर्नाटक', lat: 15.32, lng: 76.71, type: 'State' },
  { geoName: 'Kerala', dbName: 'Kerala', displayName: 'Kerala', displayNameHi: 'केरल', lat: 10.85, lng: 76.27, type: 'State' },
  { geoName: 'Lakshadweep', dbName: 'Lakshadweep', displayName: 'Lakshadweep', displayNameHi: 'लक्षद्वीप', lat: 10.56, lng: 72.64, type: 'Union Territory' },
  { geoName: 'Madhya Pradesh', dbName: 'Madhya Pradesh', displayName: 'Madhya Pradesh', displayNameHi: 'मध्य प्रदेश', lat: 22.97, lng: 78.66, type: 'State' },
  { geoName: 'Maharashtra', dbName: 'Maharashtra', displayName: 'Maharashtra', displayNameHi: 'महाराष्ट्र', lat: 19.75, lng: 75.71, type: 'State' },
  { geoName: 'Manipur', dbName: 'Manipur', displayName: 'Manipur', displayNameHi: 'मणिपुर', lat: 24.66, lng: 93.91, type: 'State' },
  { geoName: 'Meghalaya', dbName: 'Meghalaya', displayName: 'Meghalaya', displayNameHi: 'मेघालय', lat: 25.47, lng: 91.37, type: 'State' },
  { geoName: 'Mizoram', dbName: 'Mizoram', displayName: 'Mizoram', displayNameHi: 'मिज़ोरम', lat: 23.16, lng: 92.91, type: 'State' },
  { geoName: 'Nagaland', dbName: 'Nagaland', displayName: 'Nagaland', displayNameHi: 'नागालैंड', lat: 26.16, lng: 94.56, type: 'State' },
  { geoName: 'Orissa', dbName: 'Odisha', displayName: 'Odisha', displayNameHi: 'ओडिशा', lat: 20.95, lng: 85.10, type: 'State' },
  { geoName: 'Puducherry', dbName: 'Puducherry', displayName: 'Puducherry', displayNameHi: 'पुडुचेरी', lat: 11.94, lng: 79.81, type: 'Union Territory' },
  { geoName: 'Punjab', dbName: 'Punjab', displayName: 'Punjab', displayNameHi: 'पंजाब', lat: 31.15, lng: 75.34, type: 'State' },
  { geoName: 'Rajasthan', dbName: 'Rajasthan', displayName: 'Rajasthan', displayNameHi: 'राजस्थान', lat: 27.02, lng: 74.22, type: 'State' },
  { geoName: 'Sikkim', dbName: 'Sikkim', displayName: 'Sikkim', displayNameHi: 'सिक्किम', lat: 27.53, lng: 88.51, type: 'State' },
  { geoName: 'Tamil Nadu', dbName: 'Tamil Nadu', displayName: 'Tamil Nadu', displayNameHi: 'तमिल नाडु', lat: 11.13, lng: 78.66, type: 'State' },
  { geoName: 'Tripura', dbName: 'Tripura', displayName: 'Tripura', displayNameHi: 'त्रिपुरा', lat: 23.94, lng: 91.99, type: 'State' },
  { geoName: 'Uttar Pradesh', dbName: 'Uttar Pradesh', displayName: 'Uttar Pradesh', displayNameHi: 'उत्तर प्रदेश', lat: 26.85, lng: 80.91, type: 'State' },
  { geoName: 'Uttaranchal', dbName: 'Uttarakhand', displayName: 'Uttarakhand', displayNameHi: 'उत्तराखंड', lat: 30.07, lng: 79.02, type: 'State' },
  { geoName: 'West Bengal', dbName: 'West Bengal', displayName: 'West Bengal', displayNameHi: 'पश्चिम बंगाल', lat: 22.99, lng: 87.75, type: 'State' },
];

// Ladakh is in the DB but not in the GeoJSON (part of J&K pre-2019)
export const LADAKH_EXTRA: StateMapping = {
  geoName: 'Ladakh',
  dbName: 'Ladakh',
  displayName: 'Ladakh',
  displayNameHi: 'लद्दाख',
  lat: 34.15,
  lng: 77.58,
  type: 'Union Territory',
};

// Lookup maps
const byGeoName = new Map<string, StateMapping>();
const byDbName = new Map<string, StateMapping>();

for (const m of STATE_MAPPINGS) {
  byGeoName.set(m.geoName, m);
  if (!byDbName.has(m.dbName)) byDbName.set(m.dbName, m);
}

export function getStateByGeoName(geoName: string): StateMapping | undefined {
  return byGeoName.get(geoName);
}

export function getStateByDbName(dbName: string): StateMapping | undefined {
  return byDbName.get(dbName);
}

export function getDbNameFromGeoName(geoName: string): string {
  return byGeoName.get(geoName)?.dbName ?? geoName;
}

export function getGeoNameFromDbName(dbName: string): string | undefined {
  return byDbName.get(dbName)?.geoName;
}

export function getAllDbNames(): string[] {
  return STATE_MAPPINGS.map(m => m.dbName);
}

// Status colors - consistent across all map components
export const STATUS_COLORS: Record<string, string> = {
  'Safe': '#4da8ff',
  'Semi-Critical': '#f0b34f',
  'Critical': '#f08a3c',
  'Over-Exploited': '#b53e3e',
  'Saline': '#9e9e9e',
  'No Data': '#374151',
};

export const STATUS_COLORS_DARK: Record<string, string> = {
  'Safe': '#2563eb',
  'Semi-Critical': '#d97706',
  'Critical': '#ea580c',
  'Over-Exploited': '#dc2626',
  'Saline': '#6b7280',
  'No Data': '#1f2937',
};

// Extraction color scale (continuous)
export function getExtractionColor(stage: number): string {
  if (stage <= 0) return STATUS_COLORS['No Data'];
  if (stage <= 70) return STATUS_COLORS['Safe'];
  if (stage <= 90) return STATUS_COLORS['Semi-Critical'];
  if (stage <= 100) return STATUS_COLORS['Critical'];
  return STATUS_COLORS['Over-Exploited'];
}

// Recharge color scale
export function getRechargeColor(recharge: number): string {
  if (!recharge || recharge <= 0) return STATUS_COLORS['No Data'];
  if (recharge >= 5000) return '#10b981';
  if (recharge >= 2000) return '#34d399';
  if (recharge >= 1000) return '#6ee7b7';
  if (recharge >= 500) return '#a7f3d0';
  return '#d1fae5';
}
