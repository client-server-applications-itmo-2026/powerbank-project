// Auto-typed from OpenAPI schema (openapi.json)

export interface UserRetrieveResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  patronymic_name: string | null;
  phone_number: string | null;
  is_stantion_admin: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  updated_at: string;
}

export interface RegisterUserRequest {
  email: string;
  password: string;
  re_password: string;
  first_name: string;
  last_name: string;
  patronymic_name: string | null;
  phone_number: string | null;
}

export interface UpdateAuthenticatedUserRequest {
  email?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  patronymic_name?: string | null;
  phone_number?: string | null;
}

export interface Point {
  lat: number;
  lon: number;
}

export interface RetrieveNearestStantionsResponseItem {
  hardware_id: string;
  location: Point;
  free_slots: number;
  available_batteries: number;
}

export interface RetrieveNearestStantionsResponse {
  count: number;
  results: RetrieveNearestStantionsResponseItem[];
}

export interface TarrifSchema {
  id: number;
  name: string;
  price_per_tick: number | null;
  description: string;
  is_active: boolean;
  created_at: string;
  update_at: string;
}

export interface StantionInfoSchema {
  hardware_id: string;
  location: Point;
}

export type RentalStatusEnum =
  | 'INITIALIZING'
  | 'ACTIVE'
  | 'WAIT_FOR_COMPLETION'
  | 'COMPLETED'
  | 'CANCELLED';

export interface RentalSchema {
  id: number;
  user_id: number;
  battery_id: string;
  tariff: TarrifSchema;
  started_at_stantion: StantionInfoSchema;
  completed_at_stantion: StantionInfoSchema | null;
  final_price: number | null;
  status: RentalStatusEnum;
  started_at: string;
  completed_at: string | null;
}

export interface PagedRentalSchema {
  items: RentalSchema[];
  count: number;
}

// GET /api/tariffs — correctly named schema
export interface TariffSchema {
  id: number;
  name: string;
  price_per_tick: number | null;
  description: string;
  is_active: boolean;
  created_at: string;
  update_at: string;
}

export interface StartRentalRequest {
  stantion_id: string;
  tariff_id: number;
}

export interface CompleteRentalRequest {
  rental_id: number;
  stantion_id: string;
}
