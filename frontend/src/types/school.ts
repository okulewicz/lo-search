export interface School {
  id: string;
  rspo_id: string | null;
  name: string;
  school_type: string | null;
  address_street: string | null;
  address_city: string | null;
  address_postcode: string | null;
  voivodeship: string | null;
  county: string | null;
  municipality: string | null;
  latitude: number | null;
  longitude: number | null;
  website_url: string | null;
  phone: string | null;
  email: string | null;
  is_public: boolean | null;
  created_at: string;
  updated_at: string;
  profile?: SchoolProfile | null;
}

export interface SchoolProfile {
  id: string;
  school_id: string;
  class_profiles: ClassProfile[] | null;
  languages_offered: string[] | null;
  extracurricular_activities: string[] | null;
  notable_achievements: string[] | null;
  description_summary: string | null;
  extracted_at: string;
  model_used: string | null;
}

export interface ClassProfile {
  name: string;
  description?: string;
  languages?: string[];
}

export interface SchoolListResponse {
  items: School[];
  total: number;
  page: number;
  size: number;
}
