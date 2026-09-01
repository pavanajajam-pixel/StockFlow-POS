const API = "http://127.0.0.1:5000/api";
let products = [];
let customers = [];
let cart = [];
let paymentMethod = "Cash";
const TAX_RATE = 0.05;

document.addEventListener("DOMContentLoaded", async () => {
    setDate();
    setupPayment();
    document.getElementById("addItemBtn")?.addEventListener("click", addItem);
    document.getElementById("clearBillBtn")?.addEventListener("click", clearBill);
    document.getElementById("completeBillBtn")?.addEventListener("click", completeBill);
    document.getElementById("cancelBillBtn")?.addEventListener("click", () => location.reload());
    document.getElementById("productSelect")?.addEventListener("change", updatePrice);
    document.getElementById("customerSelect")?.addEventListener("change", updateCustomerPhone);
    await Promise.all([loadProducts(), loadCustomers(), loadRecentBills()]);
    renderBill();
});

function setDate() {
    const el = document.getElementById("billDate");
    if (el) el.textContent = new Date().toLocaleDateString("en-IN", {day:"2-digit", month:"short", year:"numeric"});
}
function setupPayment() {
    document.querySelectorAll(".payment-option").forEach(option => option.addEventListener("click", () => {
        document.querySelectorAll(".payment-option").forEach(x => x.classList.remove("selected"));
        option.classList.add("selected"); paymentMethod = option.dataset.method || "Cash";
    }));
}
async function loadProducts() {
    try {
        const r = await fetch(`${API}/products`); const d = await r.json();
        if (!r.ok || !d.success) throw new Error(d.message || "Unable to load products.");
        products = d.products || [];
        const select = document.getElementById("productSelect"); if (!select) return;
        select.innerHTML = '<option value="">Select Product</option>';
        products.filter(p => Number(p.quantity) > 0).forEach(p => {
            const o = document.createElement("option"); o.value = p.id; o.textContent = `${p.description} - ₹${Number(p.price).toFixed(2)} (Stock: ${p.quantity})`; o.dataset.price = p.price; o.dataset.name = p.description; o.dataset.stock = p.quantity; select.appendChild(o);
        });
    } catch(e) { console.error(e); alert(e.message); }
}
async function loadCustomers() {
    try {
        const r = await fetch(`${API}/customers`); const d = await r.json();
        if (!r.ok || !d.success) throw new Error(d.message || "Unable to load customers.");
        customers = d.customers || [];
        const select = document.getElementById("customerSelect"); if (!select) return;
        select.innerHTML = '<option value="">Walk-in Customer</option>';
        customers.forEach(c => { const o=document.createElement("option"); o.value=c.id; o.textContent=`${c.name} - ${c.phone || "No phone"}`; o.dataset.phone=c.phone||""; select.appendChild(o); });
    } catch(e) { console.error(e); alert(e.message); }
}
function updatePrice() {
    const o = document.getElementById("productSelect")?.selectedOptions[0];
    const price = document.getElementById("productPrice"); if (price) price.value = o?.value ? `₹${Number(o.dataset.price).toFixed(2)}` : "";
}
function updateCustomerPhone() {
    const o=document.getElementById("customerSelect")?.selectedOptions[0]; const el=document.getElementById("customerPhone"); if(el) el.value=o?.dataset.phone||"";
}
function addItem() {
    const select=document.getElementById("productSelect"), qtyInput=document.getElementById("productQuantity"), o=select?.selectedOptions[0];
    if(!o?.value) return alert("Please select a product.");
    const qty=parseInt(qtyInput.value,10); const stock=Number(o.dataset.stock);
    if(!Number.isInteger(qty)||qty<1) return alert("Please enter a valid quantity.");
    const existing=cart.find(x=>x.id==o.value); const newQty=(existing?.quantity||0)+qty;
    if(newQty>stock) return alert(`Only ${stock} units are available.`);
    if(existing) existing.quantity=newQty; else cart.push({id:o.value, product_number:Number(o.value), name:o.dataset.name, price:Number(o.dataset.price), quantity:qty});
    renderBill(); select.value=""; qtyInput.value=1; updatePrice();
}
function renderBill() {
    const body=document.getElementById("billItems"); if(!body) return;
    if(!cart.length){ body.innerHTML='<tr><td colspan="5" class="empty-row">No products added yet.</td></tr>'; updateTotals(); return; }
    body.innerHTML=cart.map((item,i)=>`<tr><td>${escapeHTML(item.name)}</td><td><input type="number" min="1" value="${item.quantity}" data-i="${i}" class="bill-quantity"></td><td>₹${item.price.toFixed(2)}</td><td>₹${(item.price*item.quantity).toFixed(2)}</td><td><button class="delete-item-btn" data-i="${i}">Remove</button></td></tr>`).join("");
    body.querySelectorAll(".delete-item-btn").forEach(b=>b.onclick=()=>{cart.splice(Number(b.dataset.i),1);renderBill();});
    body.querySelectorAll(".bill-quantity").forEach(input=>input.onchange=()=>{const i=Number(input.dataset.i), n=parseInt(input.value,10); if(!n||n<1)return renderBill(); const product=products.find(p=>p.id==cart[i].id); if(product&&n>Number(product.quantity)) return alert(`Only ${product.quantity} units are available.`); cart[i].quantity=n; renderBill();});
    updateTotals();
}
function updateTotals(){const subtotal=cart.reduce((s,x)=>s+x.price*x.quantity,0), tax=subtotal*TAX_RATE, total=subtotal+tax; if(document.getElementById("subtotal"))document.getElementById("subtotal").textContent=`₹${subtotal.toFixed(2)}`; if(document.getElementById("tax"))document.getElementById("tax").textContent=`₹${tax.toFixed(2)}`; if(document.getElementById("grandTotal"))document.getElementById("grandTotal").textContent=`₹${total.toFixed(2)}`;}
function clearBill(){if(!cart.length)return;if(confirm("Are you sure you want to clear this bill?")){cart=[];renderBill();}}
async function completeBill(){
    if(!cart.length)return alert("Please add at least one product.");
    const staffId=localStorage.getItem("staffId")||null; const customerId=document.getElementById("customerSelect")?.value||null;
    try{
        const r=await fetch(`${API}/billing`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({customer_id:customerId?Number(customerId):null,staff_id:staffId?Number(staffId):null,payment_method:paymentMethod,discount_percent:0,items:cart.map(x=>({product_number:x.product_number,quantity:x.quantity}))})});
        const d=await r.json(); if(!r.ok||!d.success)throw new Error(d.message||"Unable to complete bill.");
        const customerName = document.getElementById("customerSelect")?.selectedOptions[0]?.textContent?.split(" - ")[0] || "Walk-in Customer"; alert(`Bill completed successfully. Bill #${d.bill.bill_id}`); printInvoice({bill_id:d.bill.bill_id, customer:customerName, items:[...cart], subtotal:d.bill.subtotal, discount_amount:d.bill.discount, final_total:d.bill.final_total}); cart=[]; renderBill(); await loadProducts(); await loadRecentBills();
    }catch(e){console.error(e);alert(e.message);}
}
async function loadRecentBills(){try{const r=await fetch(`${API}/billing`),d=await r.json();if(!r.ok||!d.success)throw new Error(d.message);const body=document.getElementById("recentBills");if(!body)return;body.innerHTML=d.bills.length?d.bills.map(b=>`<tr><td>#${b.bill_id}</td><td>${escapeHTML(b.customer)}</td><td>${b.date ? new Date(b.date).toLocaleDateString("en-IN") : "—"}</td><td>₹${Number(b.final_total).toFixed(2)}</td><td>${b.payment_method}</td><td><span class="badge bg-success">Completed</span></td></tr>`).join(""):'<tr><td colspan="6" class="empty-row">No bills available.</td></tr>';}catch(e){console.error(e);}}
function printInvoice(bill){
 const w=window.open("", "_blank", "width=800,height=700");
 if(!w)return;
 const rows=bill.items.map((x,i)=>`<tr><td>${i+1}</td><td>${escapeHTML(x.name)}</td><td>${x.quantity}</td><td>₹${Number(x.price).toFixed(2)}</td><td>₹${(Number(x.price)*x.quantity).toFixed(2)}</td></tr>`).join("");
 const tax=Number(bill.subtotal)*TAX_RATE, total=Number(bill.final_total ?? (Number(bill.subtotal)+tax));
 w.document.write(`<html><head><title>StockFlow Bill #${bill.bill_id}</title><style>body{font-family:Arial;padding:40px}h1{text-align:center;color:#5E548E}table{width:100%;border-collapse:collapse;margin-top:25px}th,td{border:1px solid #ddd;padding:10px}th{background:#5E548E;color:white}.totals{margin-left:auto;width:300px;margin-top:20px}.totals div{display:flex;justify-content:space-between;padding:6px}.grand{font-weight:bold;border-top:2px solid #5E548E}</style></head><body><h1>StockFlow</h1><h2>Invoice #${bill.bill_id}</h2><p><b>Customer:</b> ${escapeHTML(bill.customer)}</p><p><b>Date:</b> ${new Date().toLocaleString()}</p><table><thead><tr><th>#</th><th>Product</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead><tbody>${rows}</tbody></table><div class="totals"><div><span>Subtotal</span><span>₹${Number(bill.subtotal).toFixed(2)}</span></div><div><span>Tax (5%)</span><span>₹${tax.toFixed(2)}</span></div><div class="grand"><span>Total</span><span>₹${total.toFixed(2)}</span></div></div><p style="text-align:center;margin-top:50px">Thank you for shopping with StockFlow!</p><script>window.onload=()=>window.print();<\/script></body></html>`);
 w.document.close();
}
function escapeHTML(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c]));}
