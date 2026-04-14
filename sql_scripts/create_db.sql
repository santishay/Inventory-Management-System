/*
MSSQL Database.
Run this script FIRST to initialize the database.
*/

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'InventoryDB')
BEGIN
    CREATE DATABASE InventoryDB;
END
GO

USE InventoryDB;
GO