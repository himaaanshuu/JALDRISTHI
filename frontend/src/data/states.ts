export type StatusKey = "safe" | "semi" | "critical" | "over";

export interface StateData {
  name: string;
  cx: number;
  cy: number;
  lat: number;
  lng: number;
  status: StatusKey;
  ext: string;
  rech: string;
  exWater: string;
  extractable: string;
}

export const statusColor: Record<StatusKey, string> = {
  safe: "var(--safe)",
  semi: "var(--semi-critical)",
  critical: "var(--critical)",
  over: "var(--over-exploited)",
};

export const statusLabel: Record<StatusKey, string> = {
  safe: "Safe",
  semi: "Semi-Critical",
  critical: "Critical",
  over: "Over-Exploited",
};

// NOTE: Simplified overview data for the SVG map visualization.
// Actual groundwater data is sourced from CGWB and served via the API.
export const states: StateData[] = [
  { name: "Punjab", cx: 103, cy: 80, lat: 31.0, lng: 75.4, status: "critical", ext: "165%", rech: "18.4 BCM", exWater: "30.4 BCM", extractable: "20.1 BCM" },
  { name: "Haryana", cx: 113, cy: 108, lat: 29.3, lng: 76.2, status: "over", ext: "137%", rech: "10.8 BCM", exWater: "14.9 BCM", extractable: "9.4 BCM" },
  { name: "Delhi / NCR", cx: 127, cy: 119, lat: 28.6, lng: 77.2, status: "over", ext: "119%", rech: "0.28 BCM", exWater: "0.34 BCM", extractable: "0.29 BCM" },
  { name: "Rajasthan", cx: 82, cy: 151, lat: 26.6, lng: 73.8, status: "over", ext: "148%", rech: "11.6 BCM", exWater: "17.2 BCM", extractable: "11.9 BCM" },
  { name: "Uttar Pradesh", cx: 170, cy: 145, lat: 27.0, lng: 80.5, status: "semi", ext: "74%", rech: "75.2 BCM", exWater: "55.6 BCM", extractable: "70.1 BCM" },
  { name: "Gujarat", cx: 56, cy: 214, lat: 22.7, lng: 71.8, status: "semi", ext: "68%", rech: "22.7 BCM", exWater: "15.4 BCM", extractable: "21.3 BCM" },
  { name: "Madhya Pradesh", cx: 144, cy: 201, lat: 23.5, lng: 78.5, status: "safe", ext: "48%", rech: "38.4 BCM", exWater: "18.6 BCM", extractable: "36.1 BCM" },
  { name: "Maharashtra", cx: 107, cy: 266, lat: 19.5, lng: 75.7, status: "safe", ext: "41%", rech: "36.8 BCM", exWater: "15.1 BCM", extractable: "34.9 BCM" },
  { name: "Telangana", cx: 150, cy: 292, lat: 17.9, lng: 79.0, status: "semi", ext: "63%", rech: "12.1 BCM", exWater: "7.6 BCM", extractable: "11.5 BCM" },
  { name: "Andhra Pradesh", cx: 159, cy: 324, lat: 15.9, lng: 79.7, status: "semi", ext: "59%", rech: "16.4 BCM", exWater: "9.7 BCM", extractable: "15.6 BCM" },
  { name: "Karnataka", cx: 111, cy: 334, lat: 15.3, lng: 76.0, status: "safe", ext: "52%", rech: "17.9 BCM", exWater: "9.3 BCM", extractable: "16.8 BCM" },
  { name: "Tamil Nadu", cx: 146, cy: 401, lat: 11.1, lng: 78.7, status: "critical", ext: "92%", rech: "22.4 BCM", exWater: "20.6 BCM", extractable: "21.2 BCM" },
  { name: "Kerala", cx: 115, cy: 411, lat: 10.5, lng: 76.3, status: "safe", ext: "47%", rech: "6.8 BCM", exWater: "3.2 BCM", extractable: "6.4 BCM" },
  { name: "West Bengal", cx: 267, cy: 210, lat: 23.0, lng: 87.9, status: "safe", ext: "45%", rech: "30.5 BCM", exWater: "13.7 BCM", extractable: "28.9 BCM" },
  { name: "Bihar", cx: 237, cy: 168, lat: 25.6, lng: 85.6, status: "safe", ext: "39%", rech: "29.8 BCM", exWater: "11.6 BCM", extractable: "28.1 BCM" },
];

// Simplified India silhouette (Natural Earth admin-0, equirectangular projection)
export const indiaPath =
  "M391.0 124.7 L388.5 143.6 L379.1 140.7 L362.1 151.9 L348.7 195.8 L338.4 192.1 L336.3 221.2 L329.9 225.0 L319.3 199.4 L317.2 209.8 L310.0 201.4 L314.0 192.2 L319.9 191.3 L326.0 177.6 L293.7 172.9 L292.5 161.7 L275.9 153.9 L271.2 164.9 L280.7 173.4 L269.6 185.3 L277.7 189.6 L280.1 230.6 L255.0 233.8 L255.8 245.9 L192.2 306.0 L192.1 313.4 L167.6 324.0 L167.1 370.7 L161.5 386.0 L161.5 413.4 L154.7 414.2 L148.7 426.5 L152.7 431.8 L140.7 436.4 L131.0 452.0 L118.6 436.9 L90.3 344.7 L78.4 322.6 L66.5 236.0 L47.4 245.7 L38.1 243.7 L21.0 224.2 L27.3 218.4 L8.0 198.4 L16.7 187.6 L45.7 187.6 L34.2 153.2 L25.6 145.9 L40.1 129.0 L55.3 130.3 L90.0 80.8 L89.8 69.3 L101.1 60.0 L81.2 27.0 L87.7 20.0 L122.2 21.6 L134.9 8.0 L149.1 26.9 L147.7 40.1 L152.5 56.6 L143.1 54.4 L146.8 72.2 L177.9 93.7 L164.5 116.1 L206.8 139.1 L224.8 141.2 L232.4 149.4 L269.3 154.4 L270.0 130.9 L278.1 127.5 L279.4 143.4 L291.4 149.5 L321.5 147.6 L322.4 137.7 L317.0 132.6 L327.6 130.5 L354.7 108.3 L365.8 112.2 L375.1 105.4 L381.3 115.5 L376.8 122.2 L391.0 124.7 Z";

export type ViewKey =
  | "overview"
  | "assistant"
  | "map"
  | "analytics"
  | "compare"
  | "reports"
  | "sources"
  | "learning"
  | "quality"
  | "profile";
