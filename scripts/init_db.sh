#!/bin/bash

DB_USER="postgres"
DB_PASS="mypassword" # insert your postgres password here
DB_NAME="osmdb"

# Create user if not exists (safe to ignore error if user exists)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# Create database if not exists
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Install postgis if not exists
sudo -u postgres psql -d $DB_NAME -tc "SELECT 1 FROM pg_extension WHERE extname = 'postgis'" | grep -q 1 || \
  sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION postgis;" || \
    sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION hstore;"