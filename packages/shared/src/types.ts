/** Доменные типы, общие для всех frontend-приложений. Согласованы с Pydantic-схемами backend. */

export type UmraborRole = "super_admin" | "admin";
export type PartnerRole = "admin" | "operator";
export type PartnerStatus = "active" | "suspended" | "archived" | "pending";
export type PackageStatus =
  | "draft" | "moderation" | "rework" | "published" | "rejected" | "withdrawn";
export type BookingStatus = "new" | "processing" | "kabul" | "completed" | "cancelled";
export type BookingSource = "click" | "mobile" | "web";
export type PaymentStatus = "pending" | "success" | "refund" | "failed";
export type PaymentChannel = "click" | "payme" | "paynet" | "card";
export type Gender = "M" | "F";
export type DocumentType = "zagran" | "id_pass";
export type MahramRelation =
  | "husband" | "wife" | "father" | "mother" | "son" | "daughter" | "brother" | "sister";
export type RoomType =
  | "SGL" | "DBL_F" | "DBL_M" | "DBL_FM"
  | "TRPL_F" | "TRPL_M" | "TRPL_FM"
  | "QUAD_F" | "QUAD_M" | "QUAD_FM"
  | "QUAD_F3" | "QUAD_M3";
export type City = "madina" | "makkah" | "jeddah" | "other";
export type ModerationDecision = "approved" | "rejected" | "rework";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
}

export interface UmraborUser {
  id: string;
  login: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  role: UmraborRole;
  is_active: boolean;
  last_login_at: string | null;
}

export interface PartnerUser {
  id: string;
  partner_id: string;
  partner_brand: string;
  login: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  role: PartnerRole;
  is_active: boolean;
  must_change_password: boolean;
  last_login_at: string | null;
}

export interface CustomerUser {
  id: string;
  phone: string;
  email: string | null;
  full_name: string | null;
  avatar_url: string | null;
}

export interface Partner {
  id: string;
  legal_name: string;
  brand: string;
  slug: string;
  city: string;
  logo_url: string | null;
  license_no: string | null;
  license_until: string | null;
  inn: string | null;
  status: PartnerStatus;
  status_changed_at: string | null;
  contact_phone: string | null;
  contact_email: string | null;
  created_at: string;
  updated_at: string;
}

export interface Hotel {
  id: string;
  name: string;
  slug: string;
  city: City;
  stars: number;
  distance_value: number | null;
  distance_unit: string;
  photos: string[];
  amenities: string[];
}

export interface Airline {
  id: string;
  name: string;
  iata: string;
  logo_color: string | null;
}

export interface PackageHotelLink {
  id: string;
  hotel_id: string;
  hotel_name: string;
  hotel_city: string;
  hotel_stars: number;
  nights: number;
  sort_order: number;
}

export interface DepartureInventoryItem {
  id: string;
  room_type: RoomType;
  capacity: number;
  sold: number;
  is_enabled: boolean;
}

export interface Departure {
  id: string;
  package_id: string;
  date_out: string;
  date_in: string;
  flight_out: string | null;
  flight_in: string | null;
  aircraft: string | null;
  baggage: string | null;
  capacity_total: number;
  sold_total: number;
  price_sgl: number | null;
  price_dbl: number | null;
  price_trpl: number | null;
  price_quad: number | null;
  is_active: boolean;
  inventory: DepartureInventoryItem[];
}

export interface Package {
  id: string;
  partner_id: string;
  partner_brand: string | null;
  name: string;
  slug: string;
  route: string[];
  duration_days: number;
  description: string | null;
  photos: string[];
  price_sgl: number | null;
  price_dbl: number | null;
  price_trpl: number | null;
  price_quad: number | null;
  status: PackageStatus;
  submitted_at: string | null;
  moderated_at: string | null;
  moderation_note: string | null;
  hotels: PackageHotelLink[];
  service_ids: string[];
  gift_ids: string[];
  departures_count: number;
  sold_total: number;
  created_at: string;
  updated_at: string;
  departures?: Departure[];
}

export interface PilgrimMini {
  id: string;
  full_name: string;
  gender: Gender;
  document_type: DocumentType;
  document_series_number: string | null;
  has_mahram: boolean;
  mahram_id: string | null;
  mahram_name: string | null;
  mahram_relation: MahramRelation | null;
}

export interface Pilgrim extends PilgrimMini {
  customer_id: string;
  last_name: string;
  first_name: string;
  middle_name: string | null;
  birth_date: string;
  avatar_url: string | null;
  document_valid_until: string | null;
  document_file_url: string | null;
  mahram_pilgrim_id: string | null;
  notes: string | null;
  created_at: string;
}

export interface Placement {
  id: string;
  room_type: RoomType;
  capacity: number;
  price_per_person_uzs: number;
  total_uzs: number;
  awaiting_co_lodger: boolean;
  pilgrim_ids: string[];
}

export interface BookingEvent {
  id: string;
  event_type: string;
  title: string;
  description: string | null;
  actor_kind: string | null;
  actor_name: string | null;
  created_at: string;
}

export interface Booking {
  id: string;
  code: string;
  partner_id: string;
  partner_brand: string | null;
  customer_id: string;
  customer_name: string | null;
  customer_phone: string | null;
  package_id: string;
  package_name: string | null;
  departure_id: string;
  departure_date_out: string | null;
  departure_date_in: string | null;
  source: BookingSource;
  click_id: string | null;
  status: BookingStatus;
  sla_deadline_at: string | null;
  total_uzs: number;
  cashback_uzs: number;
  confirmed_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  voucher_url: string | null;
  created_at: string;
  updated_at: string;
  pilgrims?: PilgrimMini[];
  placements?: Placement[];
  events?: BookingEvent[];
}

export interface Payment {
  id: string;
  code: string;
  booking_id: string;
  booking_code: string | null;
  customer_id: string;
  customer_name: string | null;
  customer_phone: string | null;
  partner_id: string;
  partner_brand: string | null;
  channel: PaymentChannel;
  amount_uzs: number;
  status: PaymentStatus;
  paid_at: string | null;
  refund_at: string | null;
  created_at: string;
}

export interface AuditLogEntry {
  id: string;
  actor_kind: string;
  actor_id: string | null;
  actor_name: string | null;
  scope_partner_id: string | null;
  action: string;
  object_kind: string;
  object_id: string | null;
  object_label: string | null;
  description: string | null;
  ip: string | null;
  meta: Record<string, unknown>;
  created_at: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
