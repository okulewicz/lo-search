import api from "./api";
import type { School, SchoolListResponse } from "../types/school";

export interface SchoolFilters {
  city?: string;
  county?: string;
  school_type?: string;
  page?: number;
  size?: number;
}

export async function fetchSchools(filters: SchoolFilters = {}): Promise<SchoolListResponse> {
  const { data } = await api.get<SchoolListResponse>("/schools/", { params: filters });
  return data;
}

export async function fetchSchool(id: string): Promise<School> {
  const { data } = await api.get<School>(`/schools/${id}`);
  return data;
}
