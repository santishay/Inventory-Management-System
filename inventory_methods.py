import pyodbc, csv, io, os
from datetime import timezone
from dotenv import load_dotenv

"""
Helper that connects to a SQL database using mssql-python
"""

def get_connection():
    load_dotenv()
    db_password = os.getenv("DB_PASSWORD")
    
    conn_str = (f"""
        DRIVER={{ODBC Driver 18 for SQL Server}};
        SERVER=127.0.0.1;
        DATABASE=InventoryDB;
        UID=sa;
        PWD={db_password};
        Encrypt=yes;
        TrustServerCertificate=yes;"""
    )
    return pyodbc.connect(conn_str)

"""
Read/Write Operations for Database and Website
"""

## ------------
## Read Operations
## ------------

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, username, password_hash, role 
        FROM Warehouse.Users 
        WHERE username = ?
        """, (username,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "password_hash": row[2],
            "role": row[3]
        }
    return None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, username, role 
        FROM Warehouse.Users 
        WHERE user_id = ?
        """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"user_id": row[0], "username": row[1], "role": row[2]}
    return None

def get_inventory_logs(item_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT log_id, action_type, quantity_changed, old_location, new_location, log_timestamp
        FROM Warehouse.InventoryLogs
        WHERE item_id = ?
        ORDER BY log_timestamp DESC
        """, item_id)

    rows = cursor.fetchall()

    logs = []

    for row in rows:
        logs.append({
            "log_id": row.log_id,
            "action_type": row.action_type,
            "quantity_changed": row.quantity_changed,
            "old_location": row.old_location,
            "new_location": row.new_location,
            "timestamp": row.log_timestamp.replace(tzinfo=timezone.utc).isoformat() if row.log_timestamp else None
        })

    conn.close()
    return logs

def get_most_active_item():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT TOP 1 i.item_name, i.item_id
        FROM Warehouse.Inventory i
        JOIN Warehouse.InventoryLogs l ON i.item_id = l.item_id
        WHERE l.log_timestamp >= DATEADD(day, -7, GETDATE())
        GROUP BY i.item_name, i.item_id
        ORDER BY COUNT(l.log_id) DESC
    """)
    
    row = cursor.fetchone()
    conn.close()
    return {"name": row.item_name, "id": row.item_id} if row else None

def get_inventory_csv_data(selected_ids=None):
    """Gathers inventory data and returns a CSV string."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if not selected_ids:
        #Export everything if none selected
        cursor.execute("SELECT item_id, item_name, location, quantity, min_stock FROM Warehouse.Inventory")
    else:
        #Export only selected items
        placeholders = ",".join("?" for _ in selected_ids)
        cursor.execute(f"SELECT item_id, item_name, location, quantity, min_stock FROM Warehouse.Inventory WHERE item_id IN ({placeholders})", *selected_ids)
    
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Item ID', 'Name', 'Location', 'Quantity', 'Min Stock'])
    for row in rows:
        writer.writerow([row.item_id, row.item_name, row.location, row.quantity, row.min_stock])
    
    return output.getvalue()

def get_item_logs_csv_data(item_id):
    ##Gathers logs for a specific item and returns a CSV string
    conn = get_connection()
    cursor = conn.cursor()

    #Get item name
    cursor.execute("SELECT item_name FROM Warehouse.Inventory WHERE item_id = ?", (item_id,))
    item_name = cursor.fetchone().item_name

    cursor.execute("""
        SELECT log_id, action_type, quantity_changed, old_location, new_location, log_timestamp
        FROM Warehouse.InventoryLogs
        WHERE item_id = ?
        ORDER BY log_timestamp DESC
    """, (item_id,))
    
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Log ID', 'Action', 'Qty Change', 'Old Location', 'New Location', 'Timestamp'])
    for r in rows:
        writer.writerow([r.log_id, r.action_type, r.quantity_changed, r.old_location or "N/A", r.new_location or "N/A", r.log_timestamp])
    
    return item_name, output.getvalue()

def scan_item(qr_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT item_id, item_name, quantity, location, status
        FROM Warehouse.Inventory
        WHERE qr_id = ?;
    """, (qr_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row: return None
    return {
        "item_id": row.item_id, 
        "name": row.item_name, 
        "quantity": row.quantity, 
        "location": row.location, 
        "status": row.status
    }

def list_inventory(status=None, search=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT item_id, item_name, description, location, quantity, status, unit_cost, min_stock
        FROM Warehouse.Inventory
        WHERE 1=1
        """

    params = []

    #Filter by status
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    #Search filter
    if search:
        query += " AND item_name LIKE ?"
        params.append(f"%{search}%")

    cursor.execute(query, params)
    rows = cursor.fetchall()

    items = []
    for row in rows:
        #Initial data
        current_status = row.status
        loc = row.location if row.location else "No Location"
        
        #Auto handle missing location status
        if not row.location or row.location.strip().lower() == "no location":
            current_status = "Pending"
        
        #Handle Min Stock (Defaults to 0 if NULL in DB)
        m_stock = row.min_stock if row.min_stock is not None else 0
            
        #Item is "Low Stock" only if:
        #   Quantity is greater than 0 (Out of stoc handled separately)
        #   Quantity is less than or equal to the Min Stock threshold
        #   Min Stock is actually set to something greater than 0
        is_low = (0 < row.quantity <= m_stock) and (m_stock > 0)

        items.append({
            "item_id": row.item_id,
            "name": row.item_name,
            "description": row.description,
            "location": loc,
            "quantity": row.quantity,
            "status": current_status,
            "unit_cost": row.unit_cost,
            "min_stock": m_stock,
            "low_stock": is_low
        })

    conn.close()
    return items

## --------- Location Handling
def get_all_locations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM Warehouse.Locations ORDER BY name")
    rows = cursor.fetchall()

    conn.close()
    return [row.name for row in rows]

def ensure_location_exists(cursor, location_name):
    if not location_name:
        return

    cursor.execute("""
        IF NOT EXISTS (
            SELECT 1 FROM Warehouse.Locations WHERE name = ?
        )
        INSERT INTO Warehouse.Locations (name)
        VALUES (?)
    """, location_name, location_name)
## --------- 

def get_item_by_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT item_id, item_name, description, qr_id, location, quantity, status, unit_cost
            FROM Warehouse.Inventory
            WHERE item_id = ?;
        """, (item_id,))

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "item_id": row.item_id,
            "item_name": row.item_name,
            "description": row.description,
            "qr_id": str(row.qr_id),
            "location": row.location,
            "quantity": row.quantity,
            "status": row.status,
            "unit_cost": row.unit_cost
        }

    finally:
        conn.close()
    
## ------------
## Write Operations
## ------------

def create_item(name, description, location, quantity, min_stock=5, unit_cost=None):
    #Handle No location
    status = "Active"
    if not location or location.strip().lower() == "no location":
        status = "Pending"
        location = "No Location"
    else:
        location = location.strip()

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        #Ensure location exists in Locations table
        ensure_location_exists(cursor, location)

        #Insert item with all fields
        cursor.execute("""
            INSERT INTO Warehouse.Inventory
            (item_name, description, location, quantity, status, unit_cost, min_stock)
            OUTPUT INSERTED.item_id
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, description, location, quantity, status, unit_cost, min_stock))

        item_id = cursor.fetchone()[0]

        #Log
        log_inventory_action(cursor, item_id, "Create", quantity, None, location)

        conn.commit()
        return item_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def log_inventory_action(cursor, item_id, action, qty_change, old_loc = None, new_loc = None):
    
    cursor.execute("""
        INSERT INTO Warehouse.Inventorylogs
        (item_id, action_type, quantity_changed, old_location, new_location)
        VALUES (?, ?, ?, ?, ?);
        """, item_id, action, qty_change, old_loc, new_loc)
        
#Soft Delete
def soft_delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Warehouse.Inventory
            SET status = 'Archived',
            last_updated = SYSDATETIME()
            WHERE item_id = ?;
            """, (item_id,))

        if cursor.rowcount == 0:
            return False
        
        
        conn.commit()
        return True

    finally:
        conn.close()

def restore_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Warehouse.Inventory
        SET status = 'Active'
        WHERE item_id = ?
    """, (item_id,))

    log_inventory_action(
        cursor,
        item_id,
        "Restore",
        0
    )

    conn.commit()
    conn.close()
        
def update_item(item_id, name, description, location, status):

    conn = get_connection()
    cursor = conn.cursor()

    #Current Values
    cursor.execute("""
        SELECT item_name, description, location, status, unit_cost
        FROM Warehouse.Inventory
        WHERE item_id = ?
    """, item_id)

    old = cursor.fetchone()

    cursor.execute("""
        UPDATE Warehouse.Inventory
        SET item_name = ?, description = ?, location = ?, quantity = ?, unit_cost = ?
        WHERE item_id = ?
    """, (name, description, location, status, item_id))

    #Logging action
    if old.status != status:
        log_inventory_action(cursor, item_id, "Update - Status", 0)

    if old.location != location:
        log_inventory_action(cursor, item_id, "Move", 0, old.location, location)

    conn.commit()
    conn.close()
    
def update_item_comprehensive(item_id, form_data):
    old = get_item_by_id(item_id)
    conn = get_connection()
    cursor = conn.cursor()
    
    new_name = form_data["item_name"]
    new_loc = form_data["location"]
    new_status = form_data["status"]
    
    #Update core record
    cursor.execute("""
        UPDATE Warehouse.Inventory
        SET item_name = ?, description = ?, location = ?, status = ?, unit_cost = ?
        WHERE item_id = ?
    """, (new_name, form_data["description"], new_loc, new_status, form_data.get("unit_cost"), item_id))

    #Logging/Location check
    if old['item_name'] != new_name:
        log_inventory_action(cursor, item_id, "Update - Name", 0)
    if old['location'] != new_loc:
        ensure_location_exists(cursor, new_loc)
        log_inventory_action(cursor, item_id, "Move", 0, old_loc=old['location'], new_loc=new_loc)
    if old['status'] != new_status:
        log_inventory_action(cursor, item_id, "Update - Status", 0)

    conn.commit()
    conn.close()
    
def adjust_quantity_log(item_id, quantity_change):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        #Update quantity directly in SQL to prevent race conditions
        cursor.execute("""
            UPDATE Warehouse.Inventory
            SET quantity = quantity + ?,
                last_updated = SYSDATETIME()
            WHERE item_id = ?
            AND quantity + ? >= 0
        """, (quantity_change, item_id, quantity_change))

        if cursor.rowcount == 0:
            conn.rollback()
            return False

        log_inventory_action(cursor, item_id, 'Adjust', quantity_change)
        
        conn.commit()
        return True
        
    finally:
        conn.close()