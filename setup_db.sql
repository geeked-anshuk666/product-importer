-- SQL script to set up the database for the product importer application
-- Run this script in your PostgreSQL database

-- Create the database
CREATE DATABASE product_importer_db;

-- Connect to the database
\c product_importer_db;

-- Create the user (if needed)
-- CREATE USER postgres WITH PASSWORD 'postgres';

-- Grant privileges
-- GRANT ALL PRIVILEGES ON DATABASE product_importer_db TO postgres;