import { useEffect, useMemo, useRef, useCallback, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap, ZoomControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  STATE_MAPPINGS,
  getStateByGeoName,
  getDbNameFromGeoName,
  STATUS_COLORS,
  getExtractionColor,
  getRechargeColor,
} from '../data/stateMap';

export interface GroundwaterRecord {
  state: string;
  district?: string;
  block?: string;
  assessment_year?: number;
  annual_groundwater_recharge?: number;
  extractable_groundwater_resource?: number;
  groundwater_extraction?: number;
  extraction_stage?: number;
  category?: string;
  latitude?: number;
  longitude?: number;
  is_demo_data?: number;
}

export type MapMode = 'status' | 'extraction' | 'recharge' | 'level' | 'quality';

interface IndiaLeafletMapProps {
  groundwaterData: Map<string, GroundwaterRecord>;
  selectedState?: string | null;
  selectedDistrict?: string | null;
  onSelectState?: (state: string) => void;
  onSelectDistrict?: (state: string, district: string) => void;
  mode?: MapMode;
  year?: number;
  onHover?: (state: string | null) => void;
  highlightStates?: string[];
  districtData?: Map<string, GroundwaterRecord>;
  showDistricts?: boolean;
}

const INDIA_CENTER: [number, number] = [22.5, 82.0];
const INDIA_BOUNDS: L.LatLngBoundsExpression = [[6.5, 68.0], [35.5, 97.5]];

function getCategoryColor(category: string | undefined): string {
  return STATUS_COLORS[category || ''] || STATUS_COLORS['No Data'];
}

function MapUpdater({
  selectedState,
}: {
  selectedState?: string | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (selectedState) {
      const mapping = STATE_MAPPINGS.find(m => m.dbName === selectedState);
      if (mapping) {
        map.flyTo([mapping.lat, mapping.lng], 6, { duration: 0.8 });
      }
    } else {
      map.flyTo(INDIA_CENTER, 5, { duration: 0.8 });
    }
  }, [selectedState, map]);

  return null;
}

function StateGeoJsonLayer({
  geojson,
  groundwaterData,
  selectedState,
  mode,
  onSelectState,
  onHover,
  highlightStates,
}: {
  geojson: any;
  groundwaterData: Map<string, GroundwaterRecord>;
  selectedState?: string | null;
  mode: MapMode;
  onSelectState?: (state: string) => void;
  onHover?: (state: string | null) => void;
  highlightStates?: string[];
}) {
  const geoJsonRef = useRef<L.GeoJSON | null>(null);
  const [ready, setReady] = useState(false);

  const stateColors = useMemo(() => {
    const colors: Record<string, { fill: string; border: string }> = {};
    for (const feature of geojson.features) {
      const geoName = feature.properties.NAME_1;
      const dbName = getDbNameFromGeoName(geoName);
      const record = groundwaterData.get(dbName || '');

      let fillColor = STATUS_COLORS['No Data'];
      if (record) {
        switch (mode) {
          case 'status':
            fillColor = getCategoryColor(record.category);
            break;
          case 'extraction':
            fillColor = getExtractionColor(record.extraction_stage || 0);
            break;
          case 'recharge':
            fillColor = getRechargeColor(record.annual_groundwater_recharge || 0);
            break;
          default:
            fillColor = getCategoryColor(record.category);
        }
      }

      const isSelected = dbName === selectedState;
      const isHighlighted = highlightStates?.includes(dbName || '');

      colors[geoName] = {
        fill: fillColor,
        border: isSelected ? '#ffffff' : isHighlighted ? '#fbbf24' : '#1e3a5f',
      };
    }
    return colors;
  }, [geojson, groundwaterData, selectedState, mode, highlightStates]);

  const onEachFeature = useCallback(
    (feature: any, layer: L.Layer) => {
      const geoName = feature.properties.NAME_1;
      const dbName = getDbNameFromGeoName(geoName);
      const mapping = getStateByGeoName(geoName);
      const record = groundwaterData.get(dbName || '');

      const stateName = mapping?.displayName || geoName;
      const stateNameHi = mapping?.displayNameHi || '';

      let tooltipContent = `<div style="font-family:Inter,sans-serif;min-width:180px">`;
      tooltipContent += `<div style="font-weight:700;font-size:13px;margin-bottom:4px">${stateName}</div>`;
      if (stateNameHi) {
        tooltipContent += `<div style="font-size:11px;color:#94a3b8;margin-bottom:6px">${stateNameHi}</div>`;
      }

      if (record) {
        const cat = record.category || 'No Data';
        const catColor = getCategoryColor(cat);
        tooltipContent += `<div style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;color:#fff;background:${catColor};margin-bottom:6px">${cat}</div>`;
        tooltipContent += `<div style="font-size:11px;color:#94a3b8;line-height:1.6">`;
        tooltipContent += `Year: ${record.assessment_year || 'N/A'}<br/>`;
        tooltipContent += `Stage: ${(record.extraction_stage || 0).toFixed(1)}%<br/>`;
        tooltipContent += `Recharge: ${(record.annual_groundwater_recharge || 0).toLocaleString()} MCM<br/>`;
        tooltipContent += `Extraction: ${(record.groundwater_extraction || 0).toLocaleString()} MCM`;
        tooltipContent += `</div>`;
      } else {
        tooltipContent += `<div style="font-size:11px;color:#64748b">No data available</div>`;
      }
      tooltipContent += `</div>`;

      layer.bindTooltip(tooltipContent, {
        sticky: true,
        className: 'gw-state-tooltip',
        direction: 'top',
        offset: [0, -10],
      });

      layer.on({
        mouseover: () => {
          onHover?.(dbName || null);
          (layer as L.Path).setStyle({ weight: 3, fillOpacity: 0.85 });
        },
        mouseout: () => {
          onHover?.(null);
          if (geoJsonRef.current) {
            geoJsonRef.current.resetStyle(layer as any);
          }
        },
        click: () => {
          if (dbName) onSelectState?.(dbName);
        },
      });
    },
    [groundwaterData, onSelectState, onHover]
  );

  const geoStyle = useCallback(
    (feature: any) => {
      const geoName = feature.properties.NAME_1;
      const colors = stateColors[geoName] || { fill: STATUS_COLORS['No Data'], border: '#1e3a5f' };
      const dbName = getDbNameFromGeoName(geoName);
      const isSelected = dbName === selectedState;

      return {
        fillColor: colors.fill,
        weight: isSelected ? 3 : 1.5,
        opacity: 1,
        color: colors.border,
        fillOpacity: isSelected ? 0.8 : 0.55,
      };
    },
    [stateColors, selectedState]
  );

  useEffect(() => {
    setReady(true);
  }, []);

  if (!ready) return null;

  return (
    <GeoJSON
      ref={geoJsonRef as any}
      key={`states-${mode}-${selectedState || 'none'}`}
      data={geojson}
      style={geoStyle}
      onEachFeature={onEachFeature}
    />
  );
}

function DistrictGeoJsonLayer({
  geojson,
  districtData,
  selectedState,
  selectedDistrict,
  onSelectDistrict,
}: {
  geojson: any;
  districtData: Map<string, GroundwaterRecord>;
  selectedState?: string | null;
  selectedDistrict?: string | null;
  onSelectDistrict?: (state: string, district: string) => void;
}) {
  const geoJsonRef = useRef<L.GeoJSON | null>(null);
  const [ready, setReady] = useState(false);

  const filteredGeojson = useMemo(() => {
    if (!selectedState) return null;
    return {
      ...geojson,
      features: geojson.features.filter(
        (f: any) => getDbNameFromGeoName(f.properties.NAME_1) === selectedState
      ),
    };
  }, [geojson, selectedState]);

  const geoStyle = useCallback(
    (feature: any) => {
      const districtName = feature.properties.NAME_2;
      const key = `${selectedState}::${districtName}`;
      const record = districtData.get(key);
      const isSelected = districtName === selectedDistrict;

      return {
        fillColor: record ? getCategoryColor(record.category) : STATUS_COLORS['No Data'],
        weight: isSelected ? 3 : 1,
        opacity: 1,
        color: isSelected ? '#ffffff' : '#1e3a5f',
        fillOpacity: isSelected ? 0.85 : 0.5,
      };
    },
    [districtData, selectedDistrict, selectedState]
  );

  const onEachFeature = useCallback(
    (feature: any, layer: L.Layer) => {
      const districtName = feature.properties.NAME_2;
      const key = `${selectedState}::${districtName}`;
      const record = districtData.get(key);

      let content = `<div style="font-family:Inter,sans-serif;min-width:150px">`;
      content += `<div style="font-weight:700;font-size:12px">${districtName}</div>`;
      if (record) {
        content += `<div style="font-size:11px;color:#94a3b8;margin-top:4px">`;
        content += `Category: ${record.category || 'N/A'}<br/>`;
        content += `Stage: ${(record.extraction_stage || 0).toFixed(1)}%`;
        content += `</div>`;
      } else {
        content += `<div style="font-size:11px;color:#64748b">No data</div>`;
      }
      content += `</div>`;

      layer.bindTooltip(content, { sticky: true, className: 'gw-state-tooltip' });

      layer.on({
        mouseover: () => { (layer as L.Path).setStyle({ weight: 3, fillOpacity: 0.8 }); },
        mouseout: () => { if (geoJsonRef.current) geoJsonRef.current.resetStyle(layer as any); },
        click: () => { if (selectedState) onSelectDistrict?.(selectedState, districtName); },
      });
    },
    [districtData, selectedState, onSelectDistrict]
  );

  useEffect(() => { setReady(true); }, []);

  if (!ready || !filteredGeojson || !selectedState) return null;

  return (
    <GeoJSON
      ref={geoJsonRef as any}
      key={`districts-${selectedState}`}
      data={filteredGeojson}
      style={geoStyle}
      onEachFeature={onEachFeature}
    />
  );
}

export default function IndiaLeafletMap({
  groundwaterData,
  selectedState,
  selectedDistrict,
  onSelectState,
  onSelectDistrict,
  mode = 'status',
  onHover,
  highlightStates,
  districtData,
  showDistricts = false,
}: IndiaLeafletMapProps) {
  const [statesGeo, setStatesGeo] = useState<any>(null);
  const [districtsGeo, setDistrictsGeo] = useState<any>(null);

  useEffect(() => {
    fetch('/data/india_states.geojson').then(r => r.json()).then(setStatesGeo);
  }, []);

  useEffect(() => {
    if (showDistricts && selectedState && !districtsGeo) {
      fetch('/data/india_districts.geojson').then(r => r.json()).then(setDistrictsGeo);
    }
  }, [showDistricts, selectedState, districtsGeo]);

  return (
    <MapContainer
      center={INDIA_CENTER}
      zoom={5}
      minZoom={4}
      maxZoom={12}
      maxBounds={INDIA_BOUNDS}
      maxBoundsViscosity={0.8}
      zoomControl={false}
      style={{ height: '100%', width: '100%', background: '#0a1628' }}
      className="gw-map-container"
    >
      <ZoomControl position="bottomright" />
      <TileLayer
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      <MapUpdater selectedState={selectedState} />
      {statesGeo && (
        <StateGeoJsonLayer
          geojson={statesGeo}
          groundwaterData={groundwaterData}
          selectedState={selectedState}
          mode={mode}
          onSelectState={onSelectState}
          onHover={onHover}
          highlightStates={highlightStates}
        />
      )}
      {districtsGeo && showDistricts && selectedState && (
        <DistrictGeoJsonLayer
          geojson={districtsGeo}
          districtData={districtData || new Map()}
          selectedState={selectedState}
          selectedDistrict={selectedDistrict}
          onSelectDistrict={onSelectDistrict}
        />
      )}
    </MapContainer>
  );
}
