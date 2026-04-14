document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    let currentStatus = "All";
    let currentKPI = "All";

    const tabs = document.querySelectorAll("#statusTabs .nav-link");
    const cards = document.querySelectorAll(".kpi-card");
    const searchInput = document.getElementById("inventorySearch");

    // -------------------
    // TAB FILTER
    // -------------------
    tabs.forEach(tab => {
        tab.addEventListener("click", function () {
            tabs.forEach(t => t.classList.remove("active"));
            this.classList.add("active");

            currentStatus = this.dataset.status;
            filterTable();
        });
    });

    // -------------------
    // KPI FILTER (Low / Out ONLY)
    // -------------------
    cards.forEach(card => {
        card.addEventListener("click", function () {

            if (!this.dataset.filter) {
                currentKPI = "All";
                cards.forEach(c => c.classList.remove("border-dark"));
                filterTable();
                return;
            }

            if (currentKPI === this.dataset.filter) {
                currentKPI = "All";
                this.classList.remove("border-dark");
            } else {
                cards.forEach(c => c.classList.remove("border-dark"));
                this.classList.add("border-dark");
                currentKPI = this.dataset.filter;
            }

            filterTable();
        });
    });

    // -------------------
    // MIN STOCK TOGGLE
    // -------------------
    const lowStockToggle = document.getElementById('lowStockToggle');
    const minStockWrapper = document.getElementById('minStockWrapper');
    const minStockInput = document.getElementById('min_stock_input');

    lowStockToggle.addEventListener('change', function() {
        if (this.checked) {
            // Show field and set a default threshold
            minStockWrapper.style.display = 'block';
            minStockInput.value = "5"; 
        } else {
            // Hide field and reset to 0 (effectively disabling the alert)
            minStockWrapper.style.display = 'none';
            minStockInput.value = "0";
        }
    });

    // -------------------
    // MAIN FILTER 
    // -------------------
    function filterTable() {

        const tbody = document.querySelector("#inventoryTable tbody");
        const search = searchInput.value.toLowerCase();

        //Fade OUT
        tbody.style.opacity = 0;

        setTimeout(() => {

            document.querySelectorAll("#inventoryTable tbody tr").forEach(row => {

                const status = (row.dataset.status || "").toLowerCase();
                const qty = parseFloat(row.dataset.quantity || "0");
                
                //Pull min stock from the row's data attribute
                const minStockThreshold = parseFloat(row.dataset.minStock || "0");

                const text = row.innerText.toLowerCase();

                //STATUS FILTER
                let statusMatch = (currentStatus === "All" || status === currentStatus.toLowerCase());

                //KPI FILTER (Compares against dynamic min stock)
                let kpiMatch = true;

                if (currentKPI === "Low") {
                    //Item is low if quantity is > 0 but <= its specific min stock
                    kpiMatch = qty <= minStockThreshold && qty > 0;
                } else if (currentKPI === "Out") {
                    kpiMatch = qty === 0;
                }

                //SEARCH FILTER
                let searchMatch = text.includes(search);

                row.style.display = (statusMatch && kpiMatch && searchMatch) ? "" : "none";
            });

            //Fade IN
            tbody.style.opacity = 1;

        }, 150);
    }

    // -------------------
    // SEARCH EVENTS
    // -------------------
    searchInput.addEventListener("keyup", filterTable);

    searchInput.addEventListener("keydown", function(e){
        if(e.key === "Enter") e.preventDefault();
    });

    // -------------------
    // SELECT ALL CHECKBOX
    // -------------------
    document.getElementById("selectAll").addEventListener("change", function() {
        document.querySelectorAll(".rowCheckbox").forEach(cb => {
            cb.checked = this.checked;
        });
    });

    // -------------------
    // COPY LOCATION
    // -------------------
    document.querySelectorAll(".copy-location").forEach(icon => {
        icon.addEventListener("click", function () {
            navigator.clipboard.writeText(this.dataset.location);
        });
    });

    // -------------------
    // QR Scanner
    // -------------------
    let qrScanner;

    function startScanner() {
        //Initialize the scanner instance
        qrScanner = new Html5Qrcode("qr-reader");

        //Start using back camera
        qrScanner.start(
            { facingMode: "environment" }, 
            {
                fps: 10,
                qrbox: { width: 250, height: 250 }
            },
            (decodedText) => {
                //Success = stop and redirect
                qrScanner.stop().then(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('qrScanner'));
                    if (modal) modal.hide();
                    window.location.href = decodedText;
                }).catch(err => console.error("Failed to stop scanner", err));
            }
        ).catch(err => {
            //If back camera fails (like on a laptop), try the front camera
            console.warn("Back camera not found, trying front camera...", err);
            
            qrScanner.start(
                { facingMode: "user" },
                { fps: 10, qrbox: { width: 250, height: 250 } },
                (decodedText) => {
                    qrScanner.stop().then(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('qrScanner'));
                        if (modal) modal.hide();
                        window.location.href = decodedText;
                    });
                }
            ).catch(err2 => console.error("No cameras found at all.", err2));
        });
    }

    function stopScanner() {
        if (qrScanner) {
            qrScanner.stop().catch(() => {});
        }
    }

    //Start scanner when modal opens
    document.getElementById('qrScanner').addEventListener('shown.bs.modal', startScanner);

    //Stop scanner when modal closes
    document.getElementById('qrScanner').addEventListener('hidden.bs.modal', stopScanner);


    // -------------------
    // Add Item Modal
    // -------------------
    //Automatically reset the form whenever the modal is closed/hidden
    document.getElementById('addItemModal').addEventListener('hidden.bs.modal', function () {
        this.querySelector('form').reset();
        // Also hide the min-stock wrapper if it was toggled on
        document.getElementById('minStockWrapper').style.display = 'none';
    });
});