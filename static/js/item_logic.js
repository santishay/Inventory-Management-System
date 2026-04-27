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
    const timeElements = document.querySelectorAll('.log-time');

    timeElements.forEach(element => {
        const utcString = element.dataset.timestamp;

        if (!utcString) {
            element.innerText = "N/A";
            return;
        }

        const date = new Date(utcString);

        element.innerText = date.toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: '2-digit',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });

    });
});