-- FinSight Database Initialization Script
-- This script is executed only on first container startup
-- It ensures the database and user exist with proper permissions

-- The database and user are already created via environment variables
-- This script can be used for additional initialization if needed

-- Grant all privileges on the database (already done by default, but explicit)
GRANT ALL PRIVILEGES ON DATABASE finsight_db TO finsight_user;

-- Note: Django migrations will handle table creation
-- Tables are created automatically when running:
-- python manage.py migrate
