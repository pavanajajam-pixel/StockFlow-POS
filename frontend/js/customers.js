const API_URL = "http://127.0.0.1:5000/api/customers";
let customers = [];
let editingId = null;

document.addEventListener("DOMContentLoaded", () => {
    loadCustomers();
    const form = document.getElementById("customerForm");
    if (form) form.addEventListener("submit", saveCustomer);
    const search = document.getElementById("customerSearch");
    if (search) search.addEventListener("input", () => displayCustomers(search.value));
});

async function loadCustomers() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || "Unable to load customers.");
        customers = data.customers || [];
        displayCustomers();
        updateCustomerStats();
    } catch (error) {
        console.error(error);
        const body = document.getElementById("customerTableBody");
        if (body) body.innerHTML = `<tr><td colspan="7" class="text-center py-5">Unable to load customers. Make sure Flask is running.</td></tr>`;
    }
}

async function saveCustomer(event) {
    event.preventDefault();
    const payload = {
        name: document.getElementById("customerName").value.trim(),
        phone: document.getElementById("customerPhone").value.trim(),
        email: document.getElementById("customerEmail").value.trim(),
        address: document.getElementById("customerAddress").value.trim()
    };
    if (!payload.name || !payload.phone) return alert("Please enter customer name and phone number.");
    try {
        const response = await fetch(editingId ? `${API_URL}/${editingId}` : API_URL, {
            method: editingId ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || "Customer operation failed.");
        alert(editingId ? "Customer updated successfully." : "Customer added successfully.");
        clearForm();
        const modalElement = document.getElementById("addCustomerModal");
        if (modalElement && window.bootstrap) bootstrap.Modal.getOrCreateInstance(modalElement).hide();
        await loadCustomers();
    } catch (error) { console.error(error); alert(error.message); }
}

function displayCustomers(search = "") {
    const body = document.getElementById("customerTableBody");
    if (!body) return;
    const text = String(search).toLowerCase().trim();
    const list = customers.filter(c => `${c.name} ${c.phone} ${c.email} ${c.address}`.toLowerCase().includes(text));
    body.innerHTML = list.length ? list.map(c => `
        <tr>
            <td><strong>#${c.id}</strong></td>
            <td><div class="customer-name"><div class="customer-avatar">${getInitials(c.name)}</div><span>${escapeHTML(c.name)}</span></div></td>
            <td>${escapeHTML(c.phone)}</td>
            <td>${c.email ? escapeHTML(c.email) : "—"}</td>
            <td>${c.address ? escapeHTML(c.address) : "—"}</td>
            <td><span class="badge bg-success-subtle text-success">Active</span></td>
            <td><div class="d-flex gap-2"><button class="btn btn-sm btn-outline-primary" onclick="editCustomer(${c.id})"><i class="bi bi-pencil"></i></button><button class="btn btn-sm btn-outline-danger" onclick="deleteCustomer(${c.id})"><i class="bi bi-trash"></i></button></div></td>
        </tr>`).join("") : `<tr><td colspan="7" class="text-center py-5">No customers found</td></tr>`;
}

async function editCustomer(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`);
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || "Unable to load customer.");
        const c = data.customer;
        editingId = id;
        document.getElementById("customerName").value = c.name || "";
        document.getElementById("customerPhone").value = c.phone || "";
        document.getElementById("customerEmail").value = c.email || "";
        document.getElementById("customerAddress").value = c.address || "";
        const modal = document.getElementById("addCustomerModal");
        if (modal && window.bootstrap) bootstrap.Modal.getOrCreateInstance(modal).show();
    } catch (error) { alert(error.message); }
}

async function deleteCustomer(id) {
    const c = customers.find(x => x.id === id);
    if (!c || !confirm(`Are you sure you want to delete ${c.name}?`)) return;
    try {
        const response = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.message || "Unable to delete customer.");
        alert("Customer deleted successfully.");
        await loadCustomers();
    } catch (error) { alert(error.message); }
}

function clearForm() {
    editingId = null;
    const form = document.getElementById("customerForm");
    if (form) form.reset();
}
function updateCustomerStats() {
    const total = document.getElementById("totalCustomers");
    const active = document.getElementById("activeCustomers");
    const newer = document.getElementById("newCustomers");
    if (total) total.textContent = customers.length;
    if (active) active.textContent = customers.length;
    if (newer) newer.textContent = customers.length;
}
function getInitials(name) { const p = String(name).trim().split(/\s+/); return (p[0]?.[0] || "") + (p.length > 1 ? p[p.length - 1][0] : (p[0]?.[1] || "")); }
function escapeHTML(v) { return String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c])); }
window.editCustomer = editCustomer;
window.deleteCustomer = deleteCustomer;
window.clearCustomerForm = clearForm;
