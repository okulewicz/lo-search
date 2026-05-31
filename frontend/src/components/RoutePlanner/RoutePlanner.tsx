import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { planRoute } from "../../services/routeService";
import type { RouteItinerary } from "../../types/route";
import { Bus, MapPin, Clock, ArrowRight } from "lucide-react";

interface Props {
  toLat: number;
  toLon: number;
  schoolName: string;
}

const MODE_ICON: Record<string, string> = {
  WALK: "🚶",
  BUS: "🚌",
  TRAM: "🚊",
  SUBWAY: "🚇",
  RAIL: "🚆",
  FERRY: "⛴",
};

function formatDuration(seconds: number) {
  const m = Math.round(seconds / 60);
  return m < 60 ? `${m} min` : `${Math.floor(m / 60)}h ${m % 60}min`;
}

export default function RoutePlanner({ toLat, toLon, schoolName }: Props) {
  const [fromLat, setFromLat] = useState("");
  const [fromLon, setFromLon] = useState("");

  const { mutate, data, isPending, isError } = useMutation({
    mutationFn: planRoute,
  });

  const handlePlan = () => {
    if (!fromLat || !fromLon) return;
    mutate({
      from_lat: parseFloat(fromLat),
      from_lon: parseFloat(fromLon),
      to_lat: toLat,
      to_lon: toLon,
    });
  };

  return (
    <div className="border rounded-xl p-5 space-y-4">
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <Bus className="w-5 h-5" /> Trasa do szkoły
      </h2>

      <div className="flex flex-wrap gap-2 items-end">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Szerokość geo. (start)</label>
          <input
            className="border rounded px-3 py-1 text-sm w-36"
            placeholder="52.2297"
            value={fromLat}
            onChange={(e) => setFromLat(e.target.value)}
          />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Długość geo. (start)</label>
          <input
            className="border rounded px-3 py-1 text-sm w-36"
            placeholder="21.0122"
            value={fromLon}
            onChange={(e) => setFromLon(e.target.value)}
          />
        </div>
        <button
          onClick={handlePlan}
          disabled={isPending}
          className="bg-blue-600 text-white px-4 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {isPending ? "Planowanie..." : "Zaplanuj trasę"}
        </button>
      </div>

      {isError && <p className="text-red-500 text-sm">Nie udało się zaplanować trasy.</p>}

      {data && (
        <div className="space-y-3">
          <p className="text-xs text-gray-400">
            Provider: {data.provider} · {data.itineraries.length} wariant(ów)
          </p>
          {data.itineraries.map((it, idx) => (
            <ItineraryCard key={idx} itinerary={it} />
          ))}
        </div>
      )}
    </div>
  );
}

function ItineraryCard({ itinerary }: { itinerary: RouteItinerary }) {
  return (
    <div className="border rounded-lg p-3 space-y-2 text-sm">
      <div className="flex items-center gap-4 text-gray-600">
        <span className="flex items-center gap-1">
          <Clock className="w-4 h-4" /> {formatDuration(itinerary.duration_seconds)}
        </span>
        <span>{itinerary.transfers} przesiadki</span>
        <span>🚶 {Math.round(itinerary.walk_distance_meters)} m</span>
      </div>
      <div className="flex flex-wrap items-center gap-1">
        {itinerary.legs.map((leg, i) => (
          <span key={i} className="flex items-center gap-1">
            <span title={leg.mode}>
              {MODE_ICON[leg.mode] ?? leg.mode}
              {leg.route_short_name && (
                <span className="text-xs bg-blue-100 text-blue-700 px-1 rounded ml-0.5">
                  {leg.route_short_name}
                </span>
              )}
            </span>
            {i < itinerary.legs.length - 1 && <ArrowRight className="w-3 h-3 text-gray-400" />}
          </span>
        ))}
      </div>
    </div>
  );
}
