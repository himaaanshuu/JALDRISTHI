# JALDRISTHI — Frontend UI/UX drop-in

Pure front end, no backend/API/data logic touched. Uses React + Vite with two
added packages: `leaflet` / `react-leaflet` for the real map tiles
(OpenStreetMap/CARTO — free, no API key).

## Where these go in your existing project

```
frontend/
  index.html                     → replace (only mounts #root + main.tsx)
  src/
    main.tsx                     → replace
    App.tsx                      → replace
    App.css                      → replace (design tokens + all component styles)
    index.css                    → replace (font import + base reset)
    data/
      states.ts                  → add (includes real lat/lng per state + simplified India outline)
    components/
      IndiaLeafletMap.tsx         → add (shared Leaflet map, bounded to India)
      IndiaMap.tsx                → legacy SVG map (kept, no longer used by views)
      Sidebar.tsx                 → add
      Topbar.tsx                  → add
      views/
        Overview.tsx              → add
        AIAssistant.tsx           → add
        MapView.tsx                → add
        Analytics.tsx              → add
        Compare.tsx                 → add
        Reports.tsx                 → add
        DataSources.tsx             → add
```

If you already have content in `App.tsx` / `App.css` / `index.css` you want to
keep (e.g. routing, providers, existing global styles), merge rather than
overwrite — the important part is that `App.css`'s `:root` tokens load once,
globally.

## Wiring up real data

All groundwater figures currently live in `src/data/states.ts` as placeholder
values. To connect to your backend:

1. Replace the static `states` array with a fetch/query hook (e.g. React
   Query, SWR, or a plain `useEffect`) that pulls from your CGWB/IN-GRES API
   and maps the response into the same `StateData` shape.
2. `IndiaMap` and every view component already read from that shape, so no
   further changes are needed downstream — just swap the data source.
3. The AI Assistant view (`AIAssistant.tsx`) has one hardcoded example
   exchange — replace it with your actual assistant/chat state and API calls.

## Map

Both the Overview page and Groundwater Map use `IndiaLeafletMap` — a Leaflet
map (dark CARTO/OSM tiles) locked to India's bounds via `maxBounds`. State
markers are plotted at real coordinates from `states.ts`. Clicking a selected
marker again clears the selection.

The Groundwater Map filters (year / state / category) compose together in one
pipeline in `MapView.tsx`; year scales the extraction-stage figure, state and
category narrow the visible markers.

## Notes

- Icons are inline SVG — no icon library required.
- Sidebar collapses into a drawer under 1024px width; `Topbar`'s menu button
  toggles it (already wired in `App.tsx`).
- Colors, type, and spacing all come from CSS custom properties in
  `App.css` `:root` — change values there to retheme globally. The dark
  surface used across the app (sidebar, hero search, map background) is
  `--deep-water` / `--dark-ocean`, currently `#0f172a`.
