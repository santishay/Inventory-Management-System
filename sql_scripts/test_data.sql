/*
TESTING AND MANIPULATION SCRIPT
Use this to seed the database with test data or run common manipulation queries.
WARNING: The top section will delete existing data in the tables.
*/

USE InventoryDB;
GO

-- ==========================================
-- CLEAR EXISTING DATA (For clean testing)
-- ==========================================
DELETE FROM Warehouse.InventoryLogs;
DELETE FROM Warehouse.Inventory;
DELETE FROM Warehouse.Locations;

-- Reset Identity columns back to 1
DBCC CHECKIDENT ('Warehouse.InventoryLogs', RESEED, 0);
DBCC CHECKIDENT ('Warehouse.Inventory', RESEED, 0);
DBCC CHECKIDENT ('Warehouse.Locations', RESEED, 0);
GO

-- ==========================================
-- SEED TEST DATA
-- ==========================================

-- Insert Locations
INSERT INTO Warehouse.Locations (name)
VALUES ('Aisle 1'), ('Aisle 2'), ('Receiving'), ('Shipping'), ('Backroom');

-- Insert Inventory Items
INSERT INTO Warehouse.Inventory (item_name, description, location, quantity, status, unit_cost, min_stock)
VALUES 
('Industrial Bolt', 'Heavy duty steel', 'Aisle 1', 100, 'Active', 0.50, 20),
('Logic Board v2', 'Main control unit', 'Aisle 2', 5, 'Active', 120.00, 10),
('Packing Tape', 'Bulk rolls', 'Receiving', 0, 'Pending', 2.99, 5);

-- Insert Sample Logs
INSERT INTO Warehouse.InventoryLogs (item_id, action_type, quantity_changed, old_location, new_location, unit_cost)
VALUES 
(1, 'Create', 100, NULL, 'Aisle 1', 0.50),
(2, 'Adjust', -2, 'Aisle 2', 'Aisle 2', 120.00);

GO

-- Quick verification
SELECT * FROM Warehouse.Inventory;
SELECT * FROM Warehouse.InventoryLogs;