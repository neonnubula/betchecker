#!/bin/bash

# AFL Statistics Database Initialization Script
# This script creates the SQLite database and sets up the schema

DB_NAME="afl_stats.db"
SCHEMA_FILE="schema.sql"

echo "=================================="
echo "AFL Stats Database Setup"
echo "=================================="
echo ""

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Error: $SCHEMA_FILE not found!"
    exit 1
fi

# Check if database already exists
if [ -f "$DB_NAME" ]; then
    echo "⚠️  Warning: $DB_NAME already exists!"
    read -p "Do you want to delete it and create a new one? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        rm "$DB_NAME"
        echo "✓ Existing database deleted"
    else
        echo "Aborted. Database not modified."
        exit 0
    fi
fi

# Create the database
echo ""
echo "Creating database: $DB_NAME"
sqlite3 "$DB_NAME" < "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Database created successfully!"
    echo ""
    echo "Database file: $DB_NAME"
    echo ""
    echo "To start using the database:"
    echo "  sqlite3 $DB_NAME"
    echo ""
    echo "Useful commands:"
    echo "  .tables                  - List all tables"
    echo "  .schema player_game_stats - View table structure"
    echo "  .headers on              - Show column headers"
    echo "  .mode column             - Format output as columns"
    echo ""
else
    echo "❌ Error creating database!"
    exit 1
fi

