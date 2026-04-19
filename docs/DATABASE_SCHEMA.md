# Database Schema (Phase 1 + Phase 2)

## Entities

### donors
- id (UUID, PK)
- full_name (VARCHAR(150), NOT NULL)
- email (VARCHAR(255), NOT NULL, UNIQUE)
- phone (VARCHAR(30), NOT NULL)
- date_of_birth (DATE, NOT NULL)
- blood_type (ENUM-like VARCHAR, NOT NULL)
- medical_history (TEXT, NULL)
- is_active (BOOLEAN, NOT NULL, default true)
- created_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
- updated_at (TIMESTAMP WITH TIME ZONE, NOT NULL)

Constraints:
- age >= 18 years

### hospitals
- id (UUID, PK)
- name (VARCHAR(200), NOT NULL)
- address (TEXT, NOT NULL)
- city (VARCHAR(100), NOT NULL)
- latitude (NUMERIC(9,6), NULL)
- longitude (NUMERIC(9,6), NULL)
- contact_email (VARCHAR(255), NOT NULL)
- contact_phone (VARCHAR(30), NOT NULL)
- is_active (BOOLEAN, NOT NULL, default true)
- created_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
- updated_at (TIMESTAMP WITH TIME ZONE, NOT NULL)

Constraints:
- latitude between -90 and 90
- longitude between -180 and 180

### blood_requests
- id (UUID, PK)
- request_number (VARCHAR(50), NOT NULL, UNIQUE)
- hospital_id (UUID, NOT NULL, FK -> hospitals.id, ON DELETE RESTRICT)
- blood_type (ENUM-like VARCHAR, NOT NULL)
- component (ENUM-like VARCHAR, NOT NULL)
- units_requested (INTEGER, NOT NULL)
- urgency (ENUM-like VARCHAR, NOT NULL)
- status (ENUM-like VARCHAR, NOT NULL, default pending)
- requested_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
- fulfilled_at (TIMESTAMP WITH TIME ZONE, NULL)
- notes (TEXT, NULL)
- created_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
- updated_at (TIMESTAMP WITH TIME ZONE, NOT NULL)

Constraints:
- units_requested > 0
- fulfilled_at is NULL or fulfilled_at >= requested_at

### blood_bags
- id (UUID, PK)
- bag_number (VARCHAR(50), NOT NULL, UNIQUE)
- donor_id (UUID, NOT NULL, FK -> donors.id, ON DELETE RESTRICT)
- storage_hospital_id (UUID, NULL, FK -> hospitals.id, ON DELETE SET NULL)
- blood_request_id (UUID, NULL, FK -> blood_requests.id, ON DELETE SET NULL)
- blood_type (ENUM-like VARCHAR, NOT NULL)
- component (ENUM-like VARCHAR, NOT NULL)
- volume_ml (INTEGER, NOT NULL)
- collection_date (TIMESTAMP WITH TIME ZONE, NOT NULL)
- expiration_date (TIMESTAMP WITH TIME ZONE, NOT NULL)
- status (ENUM-like VARCHAR, NOT NULL, default collected)
- created_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
- updated_at (TIMESTAMP WITH TIME ZONE, NOT NULL)

Constraints:
- volume_ml > 0
- expiration_date > collection_date

### users
- id (UUID, PK)
- email (VARCHAR(255), NOT NULL, UNIQUE)
- password_hash (VARCHAR(255), NOT NULL)
- role (ENUM-like VARCHAR, NOT NULL) -> donor | admin | hospital
- donor_id (UUID, NULL, UNIQUE, FK -> donors.id, ON DELETE SET NULL)
- hospital_id (UUID, NULL, UNIQUE, FK -> hospitals.id, ON DELETE SET NULL)
- is_active (BOOLEAN, NOT NULL, default true)
- created_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
- updated_at (TIMESTAMP WITH TIME ZONE, NOT NULL)

## Relationship Summary

- donors (1) -> (N) blood_bags
- hospitals (1) -> (N) blood_requests
- hospitals (1) -> (N) blood_bags via storage_hospital_id
- blood_requests (1) -> (N) blood_bags via blood_request_id
- users (0..1) -> (1) donors via donor_id
- users (0..1) -> (1) hospitals via hospital_id

## Index Strategy

- donors: email (unique), blood_type
- hospitals: name, city
- blood_requests: request_number (unique), hospital_id, (blood_type, component, urgency, status)
- blood_bags: bag_number (unique), donor_id, storage_hospital_id, blood_request_id, status, expiration_date, (blood_type, component, status, expiration_date)
- users: email (unique), role
