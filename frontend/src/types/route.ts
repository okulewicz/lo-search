export interface Coordinate {
  lat: number;
  lon: number;
}

export interface RouteLeg {
  mode: string;
  route_short_name: string | null;
  headsign: string | null;
  from_name: string;
  to_name: string;
  from_coord: Coordinate;
  to_coord: Coordinate;
  distance_meters: number;
  duration_seconds: number;
  departure_time: string | null;
  arrival_time: string | null;
}

export interface RouteItinerary {
  duration_seconds: number;
  start_time: string;
  end_time: string;
  transfers: number;
  walk_distance_meters: number;
  legs: RouteLeg[];
}

export interface RouteRequest {
  from_lat: number;
  from_lon: number;
  to_lat: number;
  to_lon: number;
  departure_time?: string;
}

export interface RouteResponse {
  provider: string;
  itineraries: RouteItinerary[];
}
