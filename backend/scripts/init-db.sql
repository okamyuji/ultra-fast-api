-- PostgreSQL 17 Initial Setup Script
-- This file runs when the PostgreSQL container starts

-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for status
CREATE TYPE product_status AS ENUM ('active', 'inactive', 'archived');

-- Note: Table creation is managed by Alembic migrations
-- This file is just for initial extensions
