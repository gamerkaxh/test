// ============================================
// Flask API Tutorial - Frontend JavaScript
// ============================================

// Section Navigation
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active');
}

// Generic request helper
async function makeRequest(method, url, body = null, responseId = 'overview-response') {
    const responseBox = document.getElementById(responseId);
    responseBox.textContent = `Sending ${method} ${url}...\n`;

    try {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url);
        // For non-GET, we need to redo with proper method
        let res;
        if (method === 'GET') {
            res = response;
        } else {
            res = await fetch(url, options);
        }

        const data = await res.json();
        const statusText = res.ok ? 'SUCCESS' : 'ERROR';
        responseBox.textContent = `// ${method} ${url}\n// Status: ${res.status} (${statusText})\n\n${JSON.stringify(data, null, 2)}`;
    } catch (error) {
        responseBox.textContent = `// ERROR\n// ${error.message}`;
    }
}


// Simplified fetch helper
async function apiCall(method, url, body = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(url, options);
    const data = await res.json();
    return { status: res.status, ok: res.ok, data };
}

function displayResponse(elementId, method, url, result) {
    const box = document.getElementById(elementId);
    const statusText = result.ok ? 'SUCCESS' : 'ERROR';
    box.textContent = `// ${method} ${url}\n// Status: ${result.status} (${statusText})\n\n${JSON.stringify(result.data, null, 2)}`;
}

// ============================================
// USERS API FUNCTIONS
// ============================================

async function getUsers() {
    const role = document.getElementById('user-role-filter').value;
    let url = '/api/users';
    if (role) url += `?role=${role}`;

    const result = await apiCall('GET', url);
    displayResponse('users-list-response', 'GET', url, result);
}

async function getUser() {
    const id = document.getElementById('user-id-get').value;
    if (!id) {
        document.getElementById('user-get-response').textContent = '// Please enter a user ID';
        return;
    }
    const url = `/api/users/${id}`;
    const result = await apiCall('GET', url);
    displayResponse('user-get-response', 'GET', url, result);
}

async function createUser() {
    const name = document.getElementById('user-name').value;
    const email = document.getElementById('user-email').value;
    const role = document.getElementById('user-role').value;

    if (!name || !email) {
        document.getElementById('user-create-response').textContent = '// Please fill in name and email';
        return;
    }

    const body = { name, email, role };
    const url = '/api/users';
    const result = await apiCall('POST', url, body);
    displayResponse('user-create-response', 'POST', url, result);
}

async function deleteUser() {
    const id = document.getElementById('user-id-delete').value;
    if (!id) {
        document.getElementById('user-delete-response').textContent = '// Please enter a user ID';
        return;
    }
    const url = `/api/users/${id}`;
    const result = await apiCall('DELETE', url);
    displayResponse('user-delete-response', 'DELETE', url, result);
}


// ============================================
// PRODUCTS API FUNCTIONS
// ============================================

async function getProducts() {
    const category = document.getElementById('product-category-filter').value;
    const inStock = document.getElementById('product-stock-filter').value;

    let url = '/api/products';
    const params = [];
    if (category) params.push(`category=${category}`);
    if (inStock) params.push(`in_stock=${inStock}`);
    if (params.length) url += '?' + params.join('&');

    const result = await apiCall('GET', url);
    displayResponse('products-list-response', 'GET', url, result);
}

async function createProduct() {
    const name = document.getElementById('product-name').value;
    const price = document.getElementById('product-price').value;
    const category = document.getElementById('product-category').value;

    if (!name || !price) {
        document.getElementById('product-create-response').textContent = '// Please fill in name and price';
        return;
    }

    const body = { name, price: parseFloat(price), category, in_stock: true };
    const url = '/api/products';
    const result = await apiCall('POST', url, body);
    displayResponse('product-create-response', 'POST', url, result);
}

async function deleteProduct() {
    const id = document.getElementById('product-id-delete').value;
    if (!id) {
        document.getElementById('product-delete-response').textContent = '// Please enter a product ID';
        return;
    }
    const url = `/api/products/${id}`;
    const result = await apiCall('DELETE', url);
    displayResponse('product-delete-response', 'DELETE', url, result);
}

// ============================================
// TASKS API FUNCTIONS
// ============================================

async function getTasks() {
    const completed = document.getElementById('task-completed-filter').value;
    const priority = document.getElementById('task-priority-filter').value;

    let url = '/api/tasks';
    const params = [];
    if (completed) params.push(`completed=${completed}`);
    if (priority) params.push(`priority=${priority}`);
    if (params.length) url += '?' + params.join('&');

    const result = await apiCall('GET', url);
    displayResponse('tasks-list-response', 'GET', url, result);
}

async function createTask() {
    const title = document.getElementById('task-title').value;
    const priority = document.getElementById('task-priority').value;

    if (!title) {
        document.getElementById('task-create-response').textContent = '// Please enter a task title';
        return;
    }

    const body = { title, priority };
    const url = '/api/tasks';
    const result = await apiCall('POST', url, body);
    displayResponse('task-create-response', 'POST', url, result);
}

async function toggleTask() {
    const id = document.getElementById('task-id-toggle').value;
    if (!id) {
        document.getElementById('task-toggle-response').textContent = '// Please enter a task ID';
        return;
    }
    const url = `/api/tasks/${id}/toggle`;
    const result = await apiCall('PATCH', url);
    displayResponse('task-toggle-response', 'PATCH', url, result);
}

// ============================================
// SEARCH & STATS FUNCTIONS
// ============================================

async function searchData() {
    const query = document.getElementById('search-query').value;
    if (!query) {
        document.getElementById('search-response').textContent = '// Please enter a search term';
        return;
    }
    const url = `/api/search?q=${encodeURIComponent(query)}`;
    const result = await apiCall('GET', url);
    displayResponse('search-response', 'GET', url, result);
}

async function getStats() {
    const url = '/api/stats';
    const result = await apiCall('GET', url);
    displayResponse('stats-response', 'GET', url, result);
}

// Fix the makeRequest function for overview
async function makeRequest(method, url) {
    const result = await apiCall(method, url);
    displayResponse('overview-response', method, url, result);
}
