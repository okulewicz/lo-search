import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { fetchSchool } from "../../services/schoolService";
import RoutePlanner from "../RoutePlanner/RoutePlanner";
import SchoolMap from "../Map/SchoolMap";
import { ArrowLeft, Globe, Phone, Mail } from "lucide-react";

export default function SchoolDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: school, isLoading, isError } = useQuery({
    queryKey: ["school", id],
    queryFn: () => fetchSchool(id!),
    enabled: !!id,
  });

  if (isLoading) return <p className="p-6 text-gray-500">Ładowanie...</p>;
  if (isError || !school) return <p className="p-6 text-red-500">Nie znaleziono szkoły.</p>;

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-6">
      <Link to="/" className="text-blue-500 flex items-center gap-1 text-sm">
        <ArrowLeft className="w-4 h-4" /> Wróć do listy
      </Link>

      <div className="border rounded-xl p-5 space-y-2">
        <h1 className="text-2xl font-bold">{school.name}</h1>
        <p className="text-gray-500">{school.school_type}</p>
        <p className="text-sm">
          {[school.address_street, school.address_postcode, school.address_city].filter(Boolean).join(", ")}
        </p>
        <div className="flex flex-wrap gap-3 text-sm mt-2">
          {school.website_url && (
            <a href={school.website_url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1 text-blue-500">
              <Globe className="w-4 h-4" /> Strona szkoły
            </a>
          )}
          {school.phone && (
            <span className="flex items-center gap-1 text-gray-600">
              <Phone className="w-4 h-4" /> {school.phone}
            </span>
          )}
          {school.email && (
            <a href={`mailto:${school.email}`} className="flex items-center gap-1 text-gray-600">
              <Mail className="w-4 h-4" /> {school.email}
            </a>
          )}
        </div>
      </div>

      {/* AI-extracted profile */}
      {school.profile && (
        <div className="border rounded-xl p-5 space-y-3">
          <h2 className="text-lg font-semibold">Profil szkoły (AI)</h2>
          {school.profile.description_summary && (
            <p className="text-sm text-gray-700">{school.profile.description_summary}</p>
          )}
          {school.profile.class_profiles && school.profile.class_profiles.length > 0 && (
            <div>
              <h3 className="font-medium text-sm mb-1">Profile klas</h3>
              <ul className="list-disc pl-4 text-sm space-y-1">
                {school.profile.class_profiles.map((cp, i) => (
                  <li key={i}>
                    <span className="font-medium">{cp.name}</span>
                    {cp.languages && cp.languages.length > 0 && (
                      <span className="text-gray-500"> – {cp.languages.join(", ")}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {school.profile.languages_offered && school.profile.languages_offered.length > 0 && (
            <p className="text-sm">
              <span className="font-medium">Języki: </span>
              {school.profile.languages_offered.join(", ")}
            </p>
          )}
          {school.profile.extracurricular_activities && school.profile.extracurricular_activities.length > 0 && (
            <div>
              <h3 className="font-medium text-sm mb-1">Zajęcia pozalekcyjne</h3>
              <p className="text-sm text-gray-700">{school.profile.extracurricular_activities.join(", ")}</p>
            </div>
          )}
        </div>
      )}

      {/* Map */}
      {school.latitude && school.longitude && (
        <SchoolMap lat={school.latitude} lon={school.longitude} name={school.name} />
      )}

      {/* Route planner */}
      {school.latitude && school.longitude && (
        <RoutePlanner
          toLat={school.latitude}
          toLon={school.longitude}
          schoolName={school.name}
        />
      )}
    </div>
  );
}
