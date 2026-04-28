/**
 * item_logic.js
 * Handles front-end quantity adjustments for the SnekSort Inventory system.
 * Uses a 'delta' system to calculate changes before sending to the Flask backend.
 * Also handles time in "Recent History"
 */

document.addEventListener('DOMContentLoaded', () => {

    //UI elements
    const section = document.getElementById('quantity-adjustment-section');
    if (!section) return;

    const display = document.getElementById('deltaDisplay');
    const hiddenInput = document.getElementById('finalDelta');
    const saveBtn = document.getElementById('saveBtn');
    const newTotalPreview = document.getElementById('newTotalPreview');
    
    const btnPlus = document.getElementById('btn-plus');
    const btnMinus = document.getElementById('btn-minus');
    const btnReset = document.getElementById('btn-reset');

    //Initialize Data
    const startingQty = parseInt(section.dataset.startingQty) || 0;
    let currentDelta = 0;

    //Core function to change UI with currentDelta
    function refreshUI() {
        const newTotal = startingQty + currentDelta;
        btnMinus.disabled = (newTotal <= 0);

        display.innerText = (currentDelta > 0 ? '+' : '') + currentDelta;
        hiddenInput.value = currentDelta;

        //Save button and New Total preview
        saveBtn.disabled = (currentDelta === 0);
        newTotalPreview.innerText = currentDelta !== 0 ? `(New Total: ${startingQty + currentDelta})` : '';

        //Update colors based on the direction of change
        display.classList.remove('text-success', 'text-danger', 'text-primary');
        if (currentDelta > 0) display.classList.add('text-success');
        else if (currentDelta < 0) display.classList.add('text-danger');
        else display.classList.add('text-primary');
    }

    //Event Listeners
    if (btnPlus) btnPlus.addEventListener('click', () => { currentDelta++; refreshUI(); });
    if (btnMinus) btnMinus.addEventListener('click', () => { 
        const newTotal = startingQty + currentDelta;
        if (newTotal <= 0) return;

        currentDelta--; 
        refreshUI(); 
    });
    
    if (btnReset) {
        btnReset.addEventListener('click', (e) => {
            e.preventDefault(); //No page jumping
            currentDelta = 0;
            refreshUI();
        });
    }

    refreshUI();

    //Time Handling

    function timeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();

        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHr = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHr / 24);

        if (diffSec < 10) return "Just now";
        if (diffMin < 1) return "Less than a minute ago";
        if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? "s" : ""} ago`;
        if (diffHr < 24) return `${diffHr} hour${diffHr !== 1 ? "s" : ""} ago`;
        if (diffDay < 7) return `${diffDay} day${diffDay !== 1 ? "s" : ""} ago`;

        return date.toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: '2-digit'
        });
    }

    const timeElements = document.querySelectorAll('.log-time');

    timeElements.forEach(element => {
        const utcString = element.dataset.timestamp;

        if (!utcString) {
            element.innerText = "N/A";
            return;
        }

        element.title = new Date(utcString).toLocaleString();

        element.innerText = timeAgo(utcString);

    });
});