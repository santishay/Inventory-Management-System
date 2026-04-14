/*
MSSQL tables and schema for Inventory and Inventory logs.
Run this script to initialize the database structure.
*/

USE InventoryDB;
GO 

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Warehouse')
BEGIN
    EXEC('CREATE SCHEMA Warehouse');
END
GO

-- Locations Table
IF OBJECT_ID(N'[Warehouse].[Locations]', N'U') IS NULL
BEGIN
    CREATE TABLE Warehouse.Locations (
        location_id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(100) NOT NULL
    );
END
GO

-- Inventory Table
IF OBJECT_ID(N'[Warehouse].[Inventory]', N'U') IS NULL
BEGIN
    CREATE TABLE Warehouse.Inventory (
        item_id INT IDENTITY(1,1) PRIMARY KEY,
        item_name NVARCHAR(100) NOT NULL,
        description NVARCHAR(255) NULL,
        qr_id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID(),
        location NVARCHAR(100) NULL,
        quantity INT NOT NULL DEFAULT 0,
        status NVARCHAR(50) NOT NULL DEFAULT 'Active',
        last_updated DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        unit_cost DECIMAL(18,2) NULL,
        min_stock INT NOT NULL DEFAULT 0,

        CONSTRAINT UQ_Inventory_QR UNIQUE (qr_id),
        CONSTRAINT CK_Inventory_Quantity CHECK (quantity >= 0)
    );
END
GO

-- Inventory Log Table
IF OBJECT_ID(N'[Warehouse].[InventoryLogs]', N'U') IS NULL
BEGIN
    CREATE TABLE Warehouse.InventoryLogs (
        log_id INT IDENTITY(1,1) PRIMARY KEY,
        item_id INT NOT NULL,
        action_type NVARCHAR(50) NOT NULL,
        quantity_changed INT NOT NULL,
        unit_cost DECIMAL(18,2) NULL,
        old_location NVARCHAR(100) NULL,
        new_location NVARCHAR(100) NULL,
        log_timestamp DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

        CONSTRAINT FK_Logs_Inventory FOREIGN KEY (item_id) REFERENCES Warehouse.Inventory(item_id)
    );
END
GO