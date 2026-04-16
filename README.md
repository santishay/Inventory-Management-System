
# Inventory-Management-System
Flask based inventory tracking system with real time stock management, logging, and dashboard analytics

## Tech Stack:
- **Backend:** Flask (Python)
- **Database:** SQL Server (Running in Docker)
- **Frontend:** Bootstrap 5 & JavaScript

## Prerequisites
- Docker: Installed and running.
- VS Code: With Python and SQL Server (mssql) extensions.
- Python 3.x & Pip: Installed and added to your PATH.
- ODBC Driver 18 for SQL Server: Installed on the host machine.

## Setup:
1. Clone the repo and make sure your Docker SQL container is running.
2. Run pip install -r requirements.txt to install dependencies.
3. Create a .env file in the root folder with DB_PASSWORD="[your_password]". Make sure there are not any spaces.
4. Run the SQL scripts in /sql_scripts (do them in order: schema, tables, data).
5. Launch by running python app.py and open a browser to 127.0.0.1:5050.

## Application Pictures
<table>
  <tr>
    <td align="center"><b>Dashboard Page</b></td>
    <td align="center"><b>Item Page</b></td>
  </tr>
  <tr>
    <td><img width="600" height="757" alt="App Screenshot of Dashboard Page" src="https://github.com/user-attachments/assets/998ed7e5-c759-44ab-9eea-3529f9ec3c8b" /></td>
    <td><img width="600" height="724" alt="App Screenshot of Item Page" src="https://github.com/user-attachments/assets/f9f7cde0-547a-4f0e-a9f8-bfe2cf653d8c" /></td>
  </tr>
</table>

## License:
This project is licensed under the AGPLv3. See the LICENSE file for more details.
