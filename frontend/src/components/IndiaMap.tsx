import { indiaPath, states, statusColor, type StateData } from "../data/states";

interface IndiaMapProps {
  dark?: boolean;
  onSelect: (state: StateData) => void;
  selected?: string | null;
  visible?: StateData[];
}

export default function IndiaMap({ dark = false, onSelect, selected, visible }: IndiaMapProps) {
  const shown = visible ?? states;
  return (
    <svg viewBox="0 0 400 480" role="img" aria-label="Groundwater categorisation map of India">
      <path className="india-poly" d={indiaPath} />
      {shown.map((s) => {
        const c = statusColor[s.status];
        return (
          <g key={s.name}>
            <circle className="state-node-ring" cx={s.cx} cy={s.cy} r={9} stroke={c} />
            <circle
              className="state-node"
              cx={s.cx}
              cy={s.cy}
              r={selected === s.name ? 7 : 5.5}
              fill={c}
              stroke={dark ? "#0F172A" : "#fff"}
              strokeWidth={1.5}
              onClick={() => onSelect(s)}
              tabIndex={0}
              role="button"
              aria-label={`${s.name}: ${s.status}`}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") onSelect(s);
              }}
            />
          </g>
        );
      })}
    </svg>
  );
}
