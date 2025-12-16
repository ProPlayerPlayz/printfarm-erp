#!/bin/bash
# create_production_users.sh
# Adds demo accounts (Admin, Operator, Ops) to the DB

# Ensure we are in the project root (or adjust path)
export FLASK_APP=wsgi.py

echo "Creating production users from demo data..."
python3 scripts/seed_demo_data.py

echo "Done! Users added:"
echo " - admin@demo.com / password"
echo " - operator@demo.com / password"
echo " - ops@demo.com / password"
