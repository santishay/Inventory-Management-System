# Copyright (C) 2026 santishay
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://gnu.org>.


from flask import Flask, request, render_template, redirect, url_for, send_file, make_response, session, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash
from datetime import timedelta
from io import BytesIO
from inventory_methods import *
import qrcode

"""
Functionality with Flask
"""

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

#Login Management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role
        
@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    
    if user_data:
        return User(user_data['user_id'], user_data['username'], user_data['role'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = get_user_by_username(username)
        
        #Verify name exists and hash matches
        if user_data and check_password_hash(user_data['password_hash'], password):
            user_object = User(user_data['user_id'], user_data['username'], user_data['role'])
            
            session.permanent = True
            
            login_user(user_object)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password. Please try again.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    search = request.args.get("search")
    
    #Item with the most logs in the last 7 days becomes most active item
    most_active = get_most_active_item() 
    items = list_inventory(status="All", search=search)
    locations = get_all_locations()

    return render_template(
        "dashboard.html",
        items=items,
        all_items=items,
        locations=locations,
        most_active=most_active
    )

@app.route("/items/<int:item_id>")
def view_item(item_id):

    item = get_item_by_id(item_id)
    locations = get_all_locations()

    if not item:
        return "Item not found", 404

    return render_template("item.html", item=item, locations=locations, logs=get_inventory_logs(item_id))

@app.route("/qr/<int:item_id>")
def generate_qr(item_id):

    item = get_item_by_id(item_id)

    if not item:
        return "Item not found", 404

    qr_data = url_for('view_item', item_id=item_id, _external=True)
    #str(item["qr_id"])  #Unique DB identifier

    #Generate QR
    qr = qrcode.make(qr_data)

    #Save to memory
    buf = BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

@app.route("/items/<int:item_id>/print")
def print_qr(item_id):

    item = get_item_by_id(item_id)

    if not item:
        return "Item not found", 404

    return render_template("print_qr.html", item=item)

@app.route("/scan")
def scan_page():
    return render_template("scan.html")
    
@app.route("/items/create", methods=["POST"])
def create_item_modal():
    #Extract data from form
    name = request.form["name"]
    description = request.form.get("description", "")
    location = request.form.get("location", "")
    quantity = int(request.form.get("quantity", 1))
    min_stock = int(request.form.get("min_stock", 5))
    
    unit_cost_raw = request.form.get("unit_cost")
    unit_cost = float(unit_cost_raw) if unit_cost_raw else None

    #Create item
    item_id = create_item(name, description, location, quantity, min_stock, unit_cost)

    #Redirect to the new item's page
    return redirect(url_for("view_item", item_id=item_id))

@app.route("/items/<int:item_id>/adjust-quantity", methods=["POST"])
def adjust_quantity(item_id):
    
    quantity_change = int(request.form["quantity_change"])
    adjust_quantity_log(item_id, quantity_change)

    return redirect(url_for("view_item", item_id=item_id))

@app.route("/items/<int:item_id>/edit", methods=["GET","POST"])
def edit_item_modal(item_id):
    if request.method == "POST":
        update_item_comprehensive(item_id, request.form)
        return redirect(url_for("view_item", item_id=item_id))
    
    item = get_item_by_id(item_id)
    
    return render_template("edit_item.html", item=item, locations=get_all_locations())

@app.route("/items/bulk-action", methods=["POST"])
def bulk_action():
    selected = request.form.getlist("selected_items")
    action = request.form.get("action")

    if not selected and action == "archive":
        return redirect(url_for("dashboard"))

    if action == "archive":
        for item_id in selected:
            soft_delete_item(item_id)
        return redirect(url_for("dashboard"))

    elif action == "export":
        csv_body = get_inventory_csv_data(selected)
        response = make_response(csv_body)
        response.headers["Content-Disposition"] = "attachment; filename=inventory_export.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    return redirect(url_for("dashboard"))

@app.route("/items/<int:item_id>/export-logs")
def export_item_logs(item_id):
    item_name, csv_body = get_item_logs_csv_data(item_id)
    
    filename = f"Logs_{item_name.replace(' ', '_')}.csv"
    output = make_response(csv_body)
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/items/<int:item_id>/restore", methods=["POST"])
def restore_items(item_id):
    restore_item(item_id)
    return redirect(url_for('dashboard'))

@app.route("/items/<int:item_id>/delete", methods=["POST"])
def archive_items(item_id):
    soft_delete_item(item_id)
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)