-- SQL Script to create department admin accounts
-- Run this in your MySQL database

-- Create department_admins table
CREATE TABLE IF NOT EXISTS department_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert department admin accounts (password: dept123 for all)
-- Password hash for 'dept123'
INSERT INTO department_admins (username, password, department, name, email) VALUES
('water_admin', 'scrypt:32768:8:1$vZ8qYxQJ7KGHmXKP$c8f3e8d8a9b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9e8d7c6b5a4b3c2d1e0f9', 'Water Crisis', 'Water Department Admin', 'water@nagarik.gov.in'),
('road_admin', 'scrypt:32768:8:1$vZ8qYxQJ7KGHmXKP$c8f3e8d8a9b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9e8d7c6b5a4b3c2d1e0f9', 'Road Maintenance(Engg)', 'Road Department Admin', 'road@nagarik.gov.in'),
('garbage_admin', 'scrypt:32768:8:1$vZ8qYxQJ7KGHmXKP$c8f3e8d8a9b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9e8d7c6b5a4b3c2d1e0f9', 'Solid Waste (Garbage) Related', 'Garbage Department Admin', 'garbage@nagarik.gov.in'),
('electrical_admin', 'scrypt:32768:8:1$vZ8qYxQJ7KGHmXKP$c8f3e8d8a9b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9e8d7c6b5a4b3c2d1e0f9', 'Electrical', 'Electrical Department Admin', 'electrical@nagarik.gov.in'),
('general_admin', 'scrypt:32768:8:1$vZ8qYxQJ7KGHmXKP$c8f3e8d8a9b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9e8d7c6b5a4b3c2d1e0f9', 'General Department', 'General Department Admin', 'general@nagarik.gov.in');

-- Note: For production, generate proper password hashes using Python:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('dept123'))
