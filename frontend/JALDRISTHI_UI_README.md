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

## Data Sources

Groundwater data is sourced from CGWB (Central Ground Water Board) National Compilation
publications and served via the Supabase PostgreSQL backend. The `src/data/states.ts` file
contains simplified overview data for the SVG map visualization.

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
