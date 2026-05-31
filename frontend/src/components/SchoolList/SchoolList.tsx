import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";
import { fetchSchools, type SchoolFilters } from "../../services/schoolService";
import { School2, MapPin, Globe } from "lucide-react";

export default function SchoolList() {
  const [filters, setFilters] = useState<SchoolFilters>({ page: 1, size: 20 });

  const { data, isLoading, isError } = useQuery({
    queryKey: ["schools", filters],
    queryFn: () => fetchSchools(filters),
  });

  const totalPages = data ? Math.ceil(data.total / (filters.size ?? 20)) : 1;

  return (
    <div className="max-w-5xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <School2 className="w-6 h-6" /> Szkoły średnie – Mazowsze
      </h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-4">
        <input
          className="border rounded px-3 py-1 text-sm"
          placeholder="Miasto"
          onChange={(e) => setFilters((f) => ({ ...f, city: e.target.value, page: 1 }))}
        />
        <input
          className="border rounded px-3 py-1 text-sm"
          placeholder="Powiat"
          onChange={(e) => setFilters((f) => ({ ...f, county: e.target.value, page: 1 }))}
        />
        <input
          className="border rounded px-3 py-1 text-sm"
          placeholder="Typ szkoły"
          onChange={(e) => setFilters((f) => ({ ...f, school_type: e.target.value, page: 1 }))}
        />
      </div>

      {isLoading && <p className="text-gray-500">Ładowanie...</p>}
      {isError && <p className="text-red-500">Błąd pobierania danych.</p>}

      <div className="space-y-2">
        {data?.items.map((school) => (
          <Link
            key={school.id}
            to={`/schools/${school.id}`}
            className="block border rounded-lg p-3 hover:bg-gray-50 transition"
          >
            <div className="font-semibold">{school.name}</div>
            <div className="text-sm text-gray-500 flex items-center gap-1 mt-0.5">
              <MapPin className="w-3 h-3" />
              {[school.address_street, school.address_city, school.county]
                .filter(Boolean)
                .join(", ")}
            </div>
            {school.website_url && (
              <div className="text-xs text-blue-500 flex items-center gap-1 mt-0.5">
                <Globe className="w-3 h-3" /> {school.website_url}
              </div>
            )}
          </Link>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex gap-2 mt-4 justify-center">
        <button
          disabled={(filters.page ?? 1) <= 1}
          onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))}
          className="px-3 py-1 border rounded disabled:opacity-40"
        >
          ‹ Poprzednia
        </button>
        <span className="px-3 py-1 text-sm text-gray-600">
          {filters.page} / {totalPages}
        </span>
        <button
          disabled={(filters.page ?? 1) >= totalPages}
          onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))}
          className="px-3 py-1 border rounded disabled:opacity-40"
        >
          Następna ›
        </button>
      </div>
    </div>
  );
}
