#!/bin/bash

set -euo pipefail

# Config
REMOTE_HOST="100.69.28.21"
REMOTE_DB="osmdb"
LOCAL_DB="osmdb"
USER="postgres"
TABLE_FILE="tables.config"
SSH_KEY="$HOME/.ssh/git"
TRUNCATE_FIRST=false

# Parse optional --truncate flag
if [[ "${1:-}" == "--truncate" ]]; then
  TRUNCATE_FIRST=true
fi

# Validate input
if [[ ! -f $TABLE_FILE ]]; then
  echo "Missing $TABLE_FILE"
  exit 1
fi
echo "Using SSH Key from $SSH_KEY"
echo "Tables to sync from $TABLE_FILE"
echo "Truncate enabled: $TRUNCATE_FIRST"
echo

# Loop through each table
while IFS= read -r table; do
  [[ -z "$table" ]] && continue
  echo "Syncing table: $table"

  SQL_FILE="./${table}_sync.sql"
  echo "SQL file: $SQL_FILE"
  # Start SQL file
  #touch $SQL_FILE
  echo "-- Syncing $table" > "$SQL_FILE"

  # add optional TRUNCATE statement
  if $TRUNCATE_FIRST; then
    echo "TRUNCATE TABLE $table RESTART IDENTITY CASCADE;" >> "$SQL_FILE"
  fi

  # Dump table content as INSERTs
  sudo -u postgres pg_dump -U "$USER" -d "$LOCAL_DB" -t "$table" --data-only --column-inserts >> "$SQL_FILE"

  # Add ON CONFLICT clause for idempotency
  # This is crude: relies on INSERT ... VALUES ... format of --column-inserts
  # and assumes a primary key is defined
 # sed -i "s/);$/) ON CONFLICT DO NOTHING;/" "$SQL_FILE"

  # Transfer SQL to remote
  scp -i "$SSH_KEY" "$SQL_FILE" "$REMOTE_HOST:/tmp/${table}_sync.sql"

  # Test this on test db!
  # Apply SQL on remote
  REMOTE_CMD="sudo -u postgres psql -U $USER -d $REMOTE_DB -f /tmp/${table}_sync.sql && rm /tmp/${table}_sync.sql"
  ssh -n -i "$SSH_KEY" "$REMOTE_HOST" "$REMOTE_CMD" > /tmp/${table}_ssh_stdout.log 2> /tmp/${table}_ssh_stderr.log
  SSH_EXIT_CODE=$?
  cat /tmp/${table}_ssh_stdout.log
  cat /tmp/${table}_ssh_stderr.log
  if [[ $SSH_EXIT_CODE -ne 0 ]]; then
    echo "❌ Error syncing $table (exit code $SSH_EXIT_CODE)"
  else
    echo "✅ Synced $table"
  fi
 rm "$SQL_FILE"

done < "$TABLE_FILE"

echo
echo "All tables synced successfully."