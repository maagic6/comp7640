// modal_handler.js

document.addEventListener('DOMContentLoaded', function() {
    // global variables & api urls
    const vendorsApiUrl = 'http://localhost:8000/vendors/';
    const productsApiUrl = 'http://localhost:8000/products/';
    const searchApiUrlBase = 'http://localhost:8000/products/search';
    const vendorProductsApiUrlBase = 'http://localhost:8000/products/vendor/';
    const transactionsApiUrl = 'http://localhost:8000/transactions/';

    // client-side cart state
    let cart = {}; // { productId: { name, price, quantity } }

    // dom element references
    // vendor list
    const vendorList = document.getElementById('vendor-list');
    const loadingVendors = document.getElementById('loading-vendors');
    const errorVendors = document.getElementById('error-message-vendors');
    const addVendorButton = document.getElementById('add-vendor-button');
    // vendor products modal
    const modalElement = document.getElementById('vendorProductsModal');
    let vendorProductsModalInstance = null;
    const modalTitle = document.getElementById('vendorProductsModalLabel');
    const modalProductList = document.getElementById('modal-product-list');
    const loadingModal = document.getElementById('loading-modal');
    const errorModal = document.getElementById('error-message-modal');
    const addProductToVendorBtn = document.getElementById('add-product-to-vendor-button');
    // product search
    const productSearchForm = document.getElementById('product-search-form');
    const productSearchInput = document.getElementById('product-search-input');
    const searchResultsList = document.getElementById('search-results-list');
    const loadingSearch = document.getElementById('loading-search');
    const errorSearch = document.getElementById('error-message-search');
    // cart & checkout
    const cartItemCountBadge = document.getElementById('cart-item-count');
    const checkoutModalElement = document.getElementById('checkoutModal');
    let checkoutModalInstance = null;
    const checkoutCartList = document.getElementById('checkout-cart-list');
    const checkoutTotalPrice = document.getElementById('checkout-total-price');
    const checkoutForm = document.getElementById('checkout-form');
    const customerIdInput = document.getElementById('customer-id-input');
    const checkoutLoading = document.getElementById('checkout-loading');
    const checkoutError = document.getElementById('checkout-error');
    const checkoutSuccess = document.getElementById('checkout-success');
    const submitTransactionButton = document.getElementById('submit-transaction-button');
    // add vendor modal
    const addVendorModalElement = document.getElementById('addVendorModal');
    let addVendorModalInstance = null;
    const addVendorForm = document.getElementById('add-vendor-form');
    const addVendorLoading = document.getElementById('add-vendor-loading');
    const addVendorError = document.getElementById('add-vendor-error');
    const addVendorSuccess = document.getElementById('add-vendor-success');
    // add product modal
    const addProductModalElement = document.getElementById('addProductModal');
    let addProductModalInstance = null;
    const addProductForm = document.getElementById('add-product-form');
    const addProductVendorIdInput = document.getElementById('add-product-vendor-id');
    const addProductLoading = document.getElementById('add-product-loading');
    const addProductError = document.getElementById('add-product-error');
    const addProductSuccess = document.getElementById('add-product-success');

    // helper functions
    function hideElement(element) { if (element) element.style.display = 'none'; }
    function showElement(element, displayType = 'block') { if (element) element.style.display = displayType; }
    function setText(element, text) { if (element) element.textContent = text; }

    // cart management functions
    function addToCart(productId, productName, productPrice, quantityToAdd = 1) {
        productId = parseInt(productId); productPrice = parseFloat(productPrice); quantityToAdd = parseInt(quantityToAdd);
        if (isNaN(quantityToAdd) || quantityToAdd < 1) { quantityToAdd = 1; }
        if (isNaN(productId) || !productName || isNaN(productPrice)) { console.error("Invalid product data for cart:", { productId, productName, productPrice }); alert("Error: Invalid item data."); return; }
        if (cart[productId]) { cart[productId].quantity += quantityToAdd; } else { cart[productId] = { name: productName, price: productPrice, quantity: quantityToAdd }; }
        updateCartDisplay();
    }
    function updateCartDisplay() { // updates cart badge count
        let totalItems = 0; for (const id in cart) { totalItems += cart[id].quantity; }
        if (cartItemCountBadge) { if (totalItems > 0) { setText(cartItemCountBadge, totalItems); showElement(cartItemCountBadge, 'inline-block'); } else { hideElement(cartItemCountBadge); } }
    }
    function clearCart() { cart = {}; updateCartDisplay(); populateCheckoutModal(); }

    // function to render products (with quantity input & add button)
    function renderProductList(listElement, products) {
        if (!listElement) { console.error("Target list element missing!"); return; }
        listElement.innerHTML = '';
        if (!Array.isArray(products)) { listElement.innerHTML = '<li class="list-group-item text-danger">Error: Invalid data.</li>'; return; }
        if (products.length === 0) { listElement.innerHTML = '<li class="list-group-item text-muted">No products found.</li>'; return; }
        products.forEach(product => {
           const productItem = document.createElement('li'); productItem.className = 'list-group-item d-flex justify-content-between align-items-center';
           const productId = product.product_id; const productName = product.product_name || 'Unnamed'; const productPrice = parseFloat(product.price || 0); const productNature = product.products_nature || 'N/A';
           const infoDiv = document.createElement('div'); infoDiv.innerHTML = `<span>${productName} (${productNature})</span> <span class="badge bg-success rounded-pill ms-2">$${productPrice.toFixed(2)}</span>`;
           const controlsDiv = document.createElement('div'); controlsDiv.className = 'product-controls';
           const quantityInput = document.createElement('input'); quantityInput.type = 'number'; quantityInput.className = 'form-control form-control-sm product-quantity-input'; quantityInput.value = '1'; quantityInput.min = '1'; quantityInput.setAttribute('aria-label', 'Quantity');
           const addButton = document.createElement('button'); addButton.className = 'btn btn-sm btn-outline-primary add-to-cart-btn flex-shrink-0'; addButton.textContent = 'Add +'; addButton.type = 'button';
           addButton.setAttribute('data-product-id', productId); addButton.setAttribute('data-product-name', productName); addButton.setAttribute('data-product-price', productPrice);
           controlsDiv.appendChild(quantityInput); controlsDiv.appendChild(addButton);
           productItem.appendChild(infoDiv); productItem.appendChild(controlsDiv);
           listElement.appendChild(productItem);
        });
    }

    // function to load vendors
    function loadVendors() {
         if (!vendorList || !loadingVendors || !errorVendors) { console.error("Vendor DOM elements missing"); return; }
         showElement(loadingVendors); hideElement(errorVendors); setText(errorVendors, ''); vendorList.innerHTML = '<li class="list-group-item text-muted">Loading...</li>';
         fetch(vendorsApiUrl).then(response => { if (!response.ok) throw new Error(`Vendors fetch failed: ${response.statusText}`); return response.json(); })
         .then(vendors => {
             hideElement(loadingVendors); if (!Array.isArray(vendors)) throw new Error("Invalid vendor data."); vendorList.innerHTML = '';
             if (vendors.length === 0) { vendorList.innerHTML = '<li class="list-group-item text-muted">No vendors.</li>'; return; }
             vendors.forEach(vendor => {
                if (vendor.vendor_id === null || vendor.vendor_id === undefined) { console.warn("Skipping vendor missing ID:", vendor); return; }
                const li = document.createElement('li'); li.className = 'list-group-item d-flex justify-content-between align-items-center list-group-item-action';
                li.setAttribute('data-bs-toggle','modal'); li.setAttribute('data-bs-target','#vendorProductsModal');
                li.setAttribute('data-vendor-id', vendor.vendor_id); li.setAttribute('data-vendor-name', vendor.business_name || 'Unnamed Vendor');
                let vendorScoreHtml = '';
                if (vendor.customer_feedback_score !== null && vendor.customer_feedback_score !== undefined) { vendorScoreHtml = `<span class="badge bg-info rounded-pill">Score: ${parseFloat(vendor.customer_feedback_score).toFixed(1)}</span>`; }
                else { vendorScoreHtml = `<span class="badge bg-secondary rounded-pill">No Score</span>`; }
                li.innerHTML = `<div><h5 class="mb-1">${vendor.business_name || 'Unnamed Vendor'} (ID: ${vendor.vendor_id})</h5><small class="text-muted">Location: ${vendor.geographical_presence || 'N/A'}</small>${vendor.inventory ? `<br><small class="text-muted">Inv: ${vendor.inventory}</small>` : ''}</div> ${vendorScoreHtml}`;
                vendorList.appendChild(li);
             });
         }).catch(error => { console.error('Vendor load error:', error); hideElement(loadingVendors); setText(errorVendors, `Error: ${error.message}`); showElement(errorVendors); vendorList.innerHTML = '<li class="list-group-item text-danger">Failed to load.</li>'; });
    }

    // function to load products for vendor modal
    function loadProductsForVendor(vendorId, vendorName) {
        if (!modalTitle || !modalProductList || !loadingModal || !errorModal) { console.error("Vendor product modal elements missing"); return; }
        setText(modalTitle, `Products for ${vendorName} (ID: ${vendorId})`); modalProductList.innerHTML = ''; hideElement(errorModal); setText(errorModal, ''); showElement(loadingModal);
        if(addProductToVendorBtn) { addProductToVendorBtn.setAttribute('data-vendor-id', vendorId); } else { console.warn("Add product button not found in vendor modal"); }
        fetch(`${vendorProductsApiUrlBase}${vendorId}`).then(response => { if (!response.ok) { if(response.status === 404) throw new Error(`No products found for vendor ${vendorId}.`); throw new Error(`Fetch failed: ${response.statusText}`); } return response.json(); })
        .then(products => { hideElement(loadingModal); renderProductList(modalProductList, products); }).catch(error => { console.error(`Product load error V${vendorId}:`, error); hideElement(loadingModal); setText(errorModal, `Error: ${error.message}`); showElement(errorModal); modalProductList.innerHTML = '<li class="list-group-item text-danger">Failed.</li>'; });
    }

    // function to handle product search
    function handleProductSearch(event) {
         event.preventDefault(); if (!productSearchInput || !searchResultsList || !loadingSearch || !errorSearch) { console.error("Search elements missing"); return; }
         const query = productSearchInput.value.trim(); searchResultsList.innerHTML = ''; hideElement(errorSearch); setText(errorSearch, '');
         const initialMsg = searchResultsList.querySelector('.initial-search-message'); if(initialMsg) initialMsg.remove();
         if (!query) { searchResultsList.innerHTML = '<li class="list-group-item text-muted">Enter search term.</li>'; return; } showElement(loadingSearch);
         fetch(`${searchApiUrlBase}?q=${encodeURIComponent(query)}`).then(response => { if (!response.ok) throw new Error(`Search failed: ${response.statusText}`); return response.json(); })
         .then(products => { hideElement(loadingSearch); renderProductList(searchResultsList, products); }).catch(error => { console.error('Search error:', error); hideElement(loadingSearch); setText(errorSearch, `Error: ${error.message}`); showElement(errorSearch); searchResultsList.innerHTML = '<li class="list-group-item text-danger">Failed.</li>'; });
    }

    // function to populate checkout modal
    function populateCheckoutModal() {
        if (!checkoutCartList || !checkoutTotalPrice || !submitTransactionButton) { console.error("Checkout modal elements missing!"); return;}
        checkoutCartList.innerHTML = ''; let totalPrice = 0; let itemCount = 0; const productIds = Object.keys(cart);
        if (productIds.length === 0) { checkoutCartList.innerHTML = '<li class="list-group-item text-muted">Cart empty.</li>'; submitTransactionButton.disabled = true; }
        else { productIds.forEach(id => { const item = cart[id]; const sub = item.price * item.quantity; totalPrice += sub; itemCount += item.quantity; const li = document.createElement('li'); li.className='list-group-item d-flex justify-content-between align-items-center cart-item-details'; li.innerHTML = `<span>${item.name} <small class="text-muted">Qty: ${item.quantity} @ $${item.price.toFixed(2)} ea.</small></span> <strong>$${sub.toFixed(2)}</strong>`; checkoutCartList.appendChild(li); }); submitTransactionButton.disabled = false; }
        setText(checkoutTotalPrice, totalPrice.toFixed(2));
    }

    // function to handle transaction submission
    function handleTransactionSubmit(event) {
        event.preventDefault();
        if (!checkoutForm || !customerIdInput || !checkoutLoading || !checkoutError || !checkoutSuccess || !submitTransactionButton) { console.error("Checkout form elements missing!"); return; }
        const customerId = customerIdInput.value.trim(); hideElement(checkoutError); hideElement(checkoutSuccess); setText(checkoutError, ''); setText(checkoutSuccess, '');
        if (!customerId) { setText(checkoutError, "Customer ID required."); showElement(checkoutError); return; } const custIdNum = parseInt(customerId); if (isNaN(custIdNum) || custIdNum <= 0) { setText(checkoutError, "Invalid Customer ID."); showElement(checkoutError); return; } const productIds = Object.keys(cart); if (productIds.length === 0) { setText(checkoutError, "Cart empty."); showElement(checkoutError); return; }
        const transactionData = { customer_id: custIdNum, products: productIds.map(id => ({ product_id: parseInt(id), quantity: cart[id].quantity })) };
        showElement(checkoutLoading); submitTransactionButton.disabled = true;
        fetch(transactionsApiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(transactionData) })
        .then(response => response.json().then(data => ({ status: response.status, ok: response.ok, data })))
        .then(({ status, ok, data }) => { hideElement(checkoutLoading); if (ok) { setText(checkoutSuccess, `Success! ID: ${data.transaction_id || 'N/A'}.`); showElement(checkoutSuccess); clearCart(); customerIdInput.value = ''; setTimeout(() => { if(checkoutModalInstance) checkoutModalInstance.hide(); }, 2500); } else { const errMsg = data.detail || `Request failed: ${status}`; setText(checkoutError, `Error: ${errMsg}`); showElement(checkoutError); submitTransactionButton.disabled = false; } })
        .catch(error => { console.error('Network error submitting transaction:', error); hideElement(checkoutLoading); setText(checkoutError, `Network Error: ${error.message}.`); showElement(checkoutError); submitTransactionButton.disabled = false; });
    }

    // add vendor form submission
    function handleAddVendorSubmit(event) {
        event.preventDefault(); if (!addVendorForm || !addVendorLoading || !addVendorError || !addVendorSuccess) { console.error("Add vendor form elements missing!"); return; }
        hideElement(addVendorLoading); hideElement(addVendorError); hideElement(addVendorSuccess); setText(addVendorError, ''); setText(addVendorSuccess, '');
        const vendorId = document.getElementById('new-vendor-id').value.trim(); const businessName = document.getElementById('new-vendor-name').value.trim(); const scoreInput = document.getElementById('new-vendor-score').value.trim(); const presence = document.getElementById('new-vendor-presence').value.trim(); const inventory = document.getElementById('new-vendor-inventory').value.trim();
        if (!vendorId || !businessName) { setText(addVendorError, "ID and Name required."); showElement(addVendorError); return; } const vendorIdNum = parseInt(vendorId); if (isNaN(vendorIdNum) || vendorIdNum <= 0) { setText(addVendorError, "ID must be positive number."); showElement(addVendorError); return; } let feedbackScore = null; if (scoreInput) { feedbackScore = parseFloat(scoreInput); if (isNaN(feedbackScore)) { setText(addVendorError, "Score must be number."); showElement(addVendorError); return; } }
        const vendorData = { vendor_id: vendorIdNum, business_name: businessName, customer_feedback_score: feedbackScore, geographical_presence: presence || null, inventory: inventory || null };
        showElement(addVendorLoading); const btn = addVendorForm.querySelector('button[type="submit"]'); if(btn) btn.disabled = true;
        fetch(vendorsApiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(vendorData) })
        .then(response => response.json().then(data => ({ status: response.status, ok: response.ok, data })))
        .then(({ status, ok, data }) => { hideElement(addVendorLoading); if (ok) { setText(addVendorSuccess, `Vendor "${data.business_name || 'N/A'}" added!`); showElement(addVendorSuccess); addVendorForm.reset(); loadVendors(); setTimeout(() => { hideElement(addVendorSuccess); if(addVendorModalInstance) addVendorModalInstance.hide(); }, 2000); } else { const errMsg = data.detail || `Request failed: ${status}`; setText(addVendorError, `Error: ${errMsg}`); showElement(addVendorError); if(btn) btn.disabled = false; } })
        .catch(error => { console.error("Network error adding vendor:", error); hideElement(addVendorLoading); setText(addVendorError, `Network Error: ${error.message}`); showElement(addVendorError); if(btn) btn.disabled = false; });
    }

    // add product form submission
    function handleAddProductSubmit(event) {
        event.preventDefault(); if (!addProductForm || !addProductLoading || !addProductError || !addProductSuccess || !addProductVendorIdInput) { console.error("Add product form elements missing!"); return; }
        hideElement(addProductLoading); hideElement(addProductError); hideElement(addProductSuccess); setText(addProductError, ''); setText(addProductSuccess, '');
        const productId = document.getElementById('new-product-id').value.trim(); const productName = document.getElementById('new-product-name').value.trim(); const price = document.getElementById('new-product-price').value.trim(); const nature = document.getElementById('new-product-nature').value.trim();
        const vendorId = addProductVendorIdInput.value;
        if (!productId || !productName || !price || !nature || !vendorId) { setText(addProductError, "All fields required."); showElement(addProductError); return; } const productIdNum = parseInt(productId); const priceNum = parseFloat(price); const vendorIdNum = parseInt(vendorId);
        if (isNaN(productIdNum) || productIdNum <= 0) { setText(addProductError, "Product ID invalid."); showElement(addProductError); return; } if (isNaN(priceNum) || priceNum <= 0) { setText(addProductError, "Price invalid."); showElement(addProductError); return; } if (isNaN(vendorIdNum)) { setText(addProductError, "Vendor ID missing/invalid."); showElement(addProductError); return; }
        const productData = { product_id: productIdNum, product_name: productName, price: priceNum, products_nature: nature, vendor_id: vendorIdNum };
        showElement(addProductLoading); const btn = addProductForm.querySelector('button[type="submit"]'); if(btn) btn.disabled = true;
        fetch(productsApiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(productData) })
         .then(response => response.json().then(data => ({ status: response.status, ok: response.ok, data })))
        .then(({ status, ok, data }) => { hideElement(addProductLoading); if (ok) { setText(addProductSuccess, `Product "${data.product_name || 'N/A'}" added!`); showElement(addProductSuccess); addProductForm.reset(); const vendorModalTitleText = modalTitle?.textContent || ''; const match = vendorModalTitleText.match(/\(ID: (\d+)\)/); const currentOpenVendorId = match ? parseInt(match[1]) : null; if (currentOpenVendorId) { loadProductsForVendor(currentOpenVendorId, vendorModalTitleText.split(' (ID:')[0].replace('Products for ','')); } setTimeout(() => { hideElement(addProductSuccess); if(addProductModalInstance) addProductModalInstance.hide(); }, 2000); } else { const errMsg = data.detail || `Request failed: ${status}`; setText(addProductError, `Error: ${errMsg}`); showElement(addProductError); if(btn) btn.disabled = false; } })
        .catch(error => { console.error("Network error adding product:", error); hideElement(addProductLoading); setText(addProductError, `Network Error: ${error.message}`); showElement(addProductError); if(btn) btn.disabled = false; });
    }


    // event listeners setup

    // 1. add to cart (delegation)
    document.body.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('add-to-cart-btn')) {
            const btn = event.target; if(btn.disabled) return;
            const controls = btn.closest('.product-controls'); const qtyInput = controls ? controls.querySelector('.product-quantity-input') : null; let qty = 1;
            if (qtyInput) { const pQty = parseInt(qtyInput.value); if (!isNaN(pQty) && pQty >= 1) qty = pQty; else qtyInput.value = 1; } else console.error("No qty input!");
            const id = btn.getAttribute('data-product-id'); const name = btn.getAttribute('data-product-name'); const price = btn.getAttribute('data-product-price');
            addToCart(id, name, price, qty);
            btn.textContent = 'Added!'; btn.disabled = true; setTimeout(() => { btn.textContent = 'Add +'; btn.disabled = false; }, 1000);
        }
    });

    // 2. initialize vendor products modal & listener
    if (modalElement) {
         try {
             vendorProductsModalInstance = new bootstrap.Modal(modalElement);
             modalElement.addEventListener('show.bs.modal', function (event) {
                 const trigger = event.relatedTarget; if (!trigger || typeof trigger.getAttribute !== 'function') { console.error("Invalid trigger for vendor modal"); return; }
                 const id = trigger.getAttribute('data-vendor-id'); const name = trigger.getAttribute('data-vendor-name');
                 if (id && name) {
                     if (addProductToVendorBtn) { addProductToVendorBtn.setAttribute('data-vendor-id', id); } else { console.warn("Add product button not found"); }
                     loadProductsForVendor(id, name);
                 } else { console.error("Missing vendor data attributes on modal trigger."); /* handle error display */ }
             });
         } catch(e) { console.error("Error initializing vendor products modal:", e); }
     } else { console.warn("Vendor products modal element not found."); }

    // 3. initialize checkout modal & listener
    if (checkoutModalElement) {
        try { checkoutModalInstance = new bootstrap.Modal(checkoutModalElement); checkoutModalElement.addEventListener('show.bs.modal', function() { hideElement(checkoutError); hideElement(checkoutSuccess); hideElement(checkoutLoading); populateCheckoutModal(); }); }
        catch(e) { console.error("Error initializing checkout modal:", e); }
    } else { console.warn("Checkout modal element not found."); }

    // 4. attach search form listener
    if (productSearchForm) { productSearchForm.addEventListener('submit', handleProductSearch); }
    else { console.warn("Search form not found."); }

    // 5. attach checkout form listener
    if (checkoutForm) { checkoutForm.addEventListener('submit', handleTransactionSubmit); }
    else { console.warn("Checkout form element not found."); }

    // 6. initialize add vendor modal & listener
    if (addVendorModalElement) {
        try { addVendorModalInstance = new bootstrap.Modal(addVendorModalElement); addVendorModalElement.addEventListener('show.bs.modal', function() { hideElement(addVendorError); hideElement(addVendorSuccess); hideElement(addVendorLoading); addVendorForm?.reset(); const btn = addVendorForm?.querySelector('button[type="submit"]'); if(btn) btn.disabled = false; }); }
        catch(e) { console.error("Error initializing Add Vendor modal:", e); }
    } else { console.warn("Add Vendor modal element not found."); }

    // 7. attach add vendor form listener
    if (addVendorForm) { addVendorForm.addEventListener('submit', handleAddVendorSubmit); }
    else { console.warn("Add Vendor form element not found."); }

    // 8. initialize add product modal & listener
     if (addProductModalElement) {
        try {
            addProductModalInstance = new bootstrap.Modal(addProductModalElement);
             addProductModalElement.addEventListener('show.bs.modal', function(event) {
                 hideElement(addProductError); hideElement(addProductSuccess); hideElement(addProductLoading); addProductForm?.reset(); const btn = addProductForm?.querySelector('button[type="submit"]'); if(btn) btn.disabled = false;
                 const triggerButton = event.relatedTarget; let vendorIdForForm = null;
                 if (triggerButton && typeof triggerButton.getAttribute === 'function') { vendorIdForForm = triggerButton.getAttribute('data-vendor-id'); }
                 if (addProductVendorIdInput && vendorIdForForm) { addProductVendorIdInput.value = vendorIdForForm; }
                 else { console.error("Could not set hidden vendor ID for Add Product form!", triggerButton); setText(addProductError, "Could not determine vendor."); showElement(addProductError); if(btn) btn.disabled = true; }
             });
        } catch(e) { console.error("Error initializing Add Product modal:", e); }
    } else { console.warn("Add Product modal element not found."); }

    // 9. attach add product form listener
    if (addProductForm) { addProductForm.addEventListener('submit', handleAddProductSubmit); }
    else { console.warn("Add Product form element not found."); }

    // initial page load actions
    loadVendors();
    updateCartDisplay();

});