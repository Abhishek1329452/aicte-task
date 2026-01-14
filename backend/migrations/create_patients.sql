-- Run this in Supabase SQL editor to create the `patient_sessions` table
create table if not exists public.patient_sessions (
  id uuid default gen_random_uuid() primary key,
  patient_name text,
  patient_age integer,
  patient_query text,
  ward text,
  created_at timestamptz default now()
);
