#!/bin/bash
# filepath: /home/ktodte/Documents/py_workspace/showme-backend/init_db.sh

DB_USER="postgres"
DB_PASS="mypassword" # insert your postgres password here
DB_NAME="osmdb"

sudo -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user WHERE usename = '$DB_USER'
   ) THEN
      CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
   END IF;
END
\$do\$;

DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '$DB_NAME'
   ) THEN
      CREATE DATABASE $DB_NAME OWNER $DB_USER;
   END IF;
END
\$do\$;

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\c $DB_NAME
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT 1 FROM pg_extension WHERE extname = 'postgis'
   ) THEN
      CREATE EXTENSION postgis;
   END IF;
END
\$do\$;
EOF