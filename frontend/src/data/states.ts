export type StatusKey = "safe" | "semi" | "critical" | "over";

export interface StateData {
  name: string;
  cx: number;
  cy: number;
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

// NOTE: This is stylised / placeholder data for the UI concept only.
// Replace with live values from the CGWB / IN-GRES API integration.
export const states: StateData[] = [
  { name: "Punjab", cx: 112, cy: 78, status: "critical", ext: "165%", rech: "18.4 BCM", exWater: "30.4 BCM", extractable: "20.1 BCM" },
  { name: "Haryana", cx: 135, cy: 105, status: "over", ext: "137%", rech: "10.8 BCM", exWater: "14.9 BCM", extractable: "9.4 BCM" },
  { name: "Delhi / NCR", cx: 150, cy: 112, status: "over", ext: "119%", rech: "0.28 BCM", exWater: "0.34 BCM", extractable: "0.29 BCM" },
  { name: "Rajasthan", cx: 100, cy: 150, status: "over", ext: "148%", rech: "11.6 BCM", exWater: "17.2 BCM", extractable: "11.9 BCM" },
  { name: "Uttar Pradesh", cx: 190, cy: 120, status: "semi", ext: "74%", rech: "75.2 BCM", exWater: "55.6 BCM", extractable: "70.1 BCM" },
  { name: "Gujarat", cx: 75, cy: 222, status: "semi", ext: "68%", rech: "22.7 BCM", exWater: "15.4 BCM", extractable: "21.3 BCM" },
  { name: "Madhya Pradesh", cx: 158, cy: 200, status: "safe", ext: "48%", rech: "38.4 BCM", exWater: "18.6 BCM", extractable: "36.1 BCM" },
  { name: "Maharashtra", cx: 118, cy: 262, status: "safe", ext: "41%", rech: "36.8 BCM", exWater: "15.1 BCM", extractable: "34.9 BCM" },
  { name: "Telangana", cx: 170, cy: 288, status: "semi", ext: "63%", rech: "12.1 BCM", exWater: "7.6 BCM", extractable: "11.5 BCM" },
  { name: "Andhra Pradesh", cx: 190, cy: 320, status: "semi", ext: "59%", rech: "16.4 BCM", exWater: "9.7 BCM", extractable: "15.6 BCM" },
  { name: "Karnataka", cx: 135, cy: 330, status: "safe", ext: "52%", rech: "17.9 BCM", exWater: "9.3 BCM", extractable: "16.8 BCM" },
  { name: "Tamil Nadu", cx: 170, cy: 390, status: "critical", ext: "92%", rech: "22.4 BCM", exWater: "20.6 BCM", extractable: "21.2 BCM" },
  { name: "Kerala", cx: 145, cy: 395, status: "safe", ext: "47%", rech: "6.8 BCM", exWater: "3.2 BCM", extractable: "6.4 BCM" },
  { name: "West Bengal", cx: 242, cy: 186, status: "safe", ext: "45%", rech: "30.5 BCM", exWater: "13.7 BCM", extractable: "28.9 BCM" },
  { name: "Bihar", cx: 222, cy: 150, status: "safe", ext: "39%", rech: "29.8 BCM", exWater: "11.6 BCM", extractable: "28.1 BCM" },
];

// Simplified India silhouette used by <IndiaMap />.
export const indiaPath =
  "M142 16 L160 18 L178 28 L194 24 L212 30 L226 42 L238 56 L252 54 L266 62 L274 78 L280 92 L274 108 L286 122 L292 140 L288 160 L276 174 L268 188 L276 204 L286 224 L282 242 L270 258 L258 274 L250 292 L238 312 L226 330 L214 352 L202 372 L188 392 L176 410 L164 398 L154 380 L144 360 L136 340 L128 318 L118 296 L108 274 L98 252 L88 228 L78 206 L68 190 L76 172 L88 156 L90 140 L84 124 L82 108 L88 92 L98 78 L112 66 L124 52 L132 36 Z";

export type ViewKey =
  | "overview"
  | "assistant"
  | "map"
  | "analytics"
  | "compare"
  | "reports"
  | "sources";
