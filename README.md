
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
1. Clone the repository.
2. Ensure Docker is running with the SQL Server container.
3. Install dependencies: Run pip install -r requirements.txt.
4. Create a .env file: Add DB_PASSWORD="[your_password]" (Ensure no spaces around = and use quotes).
5. Initialize Database: Run the scripts in /sql_scripts sequentially (Schema first, then Tables/Data).
6. Run `python app.py`.
7. Access the App: Open your browser and go to http://127.0.0.1:5050.

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
