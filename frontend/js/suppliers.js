// ==========================================================
// STOCKFLOW - SUPPLIERS.JS
// ==========================================================

const API_URL = "https://stockflow-pos-yorq.onrender.com/api/suppliers";

// ==========================================================
// DOM ELEMENTS
// ==========================================================

let supplierForm;
let supplierId;
let supplierName;
let supplierEmail;
let supplierProduct;
let minimumStock;

let suppliersTableBody;
let searchInput;
let clearButton;

// ==========================================================
// INITIALIZE
// ==========================================================

document.addEventListener("DOMContentLoaded", () => {

    supplierForm =
        document.getElementById("supplierForm");

    supplierId =
        document.getElementById("supplierId");

    supplierName =
        document.getElementById("supplierName");

    supplierEmail =
        document.getElementById("supplierEmail");

    supplierProduct =
        document.getElementById("supplierProduct");

    minimumStock =
        document.getElementById("minimumStock");

    suppliersTableBody =
        document.getElementById("supplierTableBody");

    searchInput =
        document.getElementById("searchSupplier");

    clearButton =
        document.getElementById("clearSupplier");


    // ------------------------------------------------------
    // Check required elements
    // ------------------------------------------------------

    if (!supplierForm) {

        console.error(
            "Supplier form (#supplierForm) was not found."
        );

        return;
    }


    // ------------------------------------------------------
    // Events
    // ------------------------------------------------------

    supplierForm.addEventListener(
        "submit",
        handleSupplierSubmit
    );


    if (clearButton) {

        clearButton.addEventListener(
            "click",
            clearForm
        );

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterSuppliers
        );

    }


    // ------------------------------------------------------
    // Load suppliers
    // ------------------------------------------------------

    loadSuppliers();

});


// ==========================================================
// LOAD SUPPLIERS
// ==========================================================

async function loadSuppliers() {

    if (!suppliersTableBody) {
        return;
    }


    try {

        const response =
            await fetch(
                API_URL,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );


        const data =
            await response
                .json()
                .catch(() => []);


        if (!response.ok) {

            throw new Error(
                data.message ||
                data.error ||
                "Unable to fetch suppliers."
            );

        }


        // Supports both:
        //
        // [
        //     {...},
        //     {...}
        // ]
        //
        // and:
        //
        // {
        //     success: true,
        //     suppliers: [...]
        // }

        const suppliers =
            Array.isArray(data)
                ? data
                : Array.isArray(data.suppliers)
                    ? data.suppliers
                    : Array.isArray(data.data)
                        ? data.data
                        : [];


        displaySuppliers(
            suppliers
        );


    } catch (error) {

        console.error(
            "Error loading suppliers:",
            error
        );


        suppliersTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    Unable to load suppliers
                </td>
            </tr>
        `;


        showMessage(
            error.message ||
            "Unable to load suppliers. Make sure the backend is running.",
            "error"
        );

    }

}


// ==========================================================
// DISPLAY SUPPLIERS
// ==========================================================

function displaySuppliers(suppliers) {

    if (!suppliersTableBody) {
        return;
    }


    suppliersTableBody.innerHTML = "";


    if (
        !Array.isArray(suppliers) ||
        suppliers.length === 0
    ) {

        suppliersTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    No suppliers found
                </td>
            </tr>
        `;

        return;
    }


    suppliers.forEach(
        supplier => {

            const row =
                document.createElement("tr");


            // Product can come as product_name
            // or product_number depending on backend.

            const productValue =
                supplier.product_name ??
                supplier.product_number ??
                "-";


            row.innerHTML = `

                <td>
                    ${escapeHTML(
                        supplier.supplier_id ?? "-"
                    )}
                </td>


                <td>
                    <strong>
                        ${escapeHTML(
                            supplier.supplier_name ?? "-"
                        )}
                    </strong>
                </td>


                <td>
                    ${escapeHTML(
                        supplier.supplier_email ?? "-"
                    )}
                </td>


                <td>
                    ${escapeHTML(
                        productValue
                    )}
                </td>


                <td>
                    ${escapeHTML(
                        supplier.minimum_stock ?? "-"
                    )}
                </td>


                <td>

                    <button
                        type="button"
                        class="table-action edit"
                        onclick="editSupplier(${Number(
                            supplier.supplier_id
                        )})"
                    >
                        Edit
                    </button>


                    <button
                        type="button"
                        class="table-action delete"
                        onclick="deleteSupplier(${Number(
                            supplier.supplier_id
                        )})"
                    >
                        Delete
                    </button>

                </td>

            `;


            suppliersTableBody.appendChild(
                row
            );

        }
    );

}


// ==========================================================
// ADD / UPDATE SUPPLIER
// ==========================================================

async function handleSupplierSubmit(event) {

    event.preventDefault();


    if (!supplierForm) {
        return;
    }


    // ------------------------------------------------------
    // Get form values
    // ------------------------------------------------------

    const name =
        supplierName.value.trim();


    const email =
        supplierEmail.value.trim();


    const product =
        supplierProduct.value.trim();


    const minimum =
        minimumStock.value.trim();


    // ------------------------------------------------------
    // Validation
    // ------------------------------------------------------

    if (
        !name ||
        !email ||
        !product ||
        minimum === ""
    ) {

        showMessage(
            "Please fill in all supplier details.",
            "error"
        );

        return;
    }


    // ------------------------------------------------------
    // Email validation
    // ------------------------------------------------------

    if (
        !email.includes("@") ||
        !email.includes(".")
    ) {

        showMessage(
            "Please enter a valid email address.",
            "error"
        );

        return;
    }


    // ------------------------------------------------------
    // Minimum stock validation
    // ------------------------------------------------------

    const minimumValue =
        Number(minimum);


    if (
        !Number.isFinite(minimumValue) ||
        minimumValue < 0
    ) {

        showMessage(
            "Minimum stock must be a valid non-negative number.",
            "error"
        );

        return;
    }


    // ------------------------------------------------------
    // Prepare supplier data
    // ------------------------------------------------------
    //
    // IMPORTANT:
    // supplierProduct is a PRODUCT NAME field.
    //
    // Therefore send:
    //
    // product_name
    //
    // NOT product_number.
    //

    const supplierData = {

        supplier_name:
            name,

        supplier_email:
            email,

        product_name:
            product,

        minimum_stock:
            minimumValue

    };


    console.log(
        "Supplier data being sent:",
        supplierData
    );


    try {

        let response;


        const isUpdate =
            Boolean(
                supplierId &&
                supplierId.value
            );


        // ==================================================
        // UPDATE SUPPLIER
        // ==================================================

        if (isUpdate) {

            response =
                await fetch(
                    `${API_URL}/${encodeURIComponent(
                        supplierId.value
                    )}`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                supplierData
                            )
                    }
                );

        }


        // ==================================================
        // ADD SUPPLIER
        // ==================================================

        else {

            response =
                await fetch(
                    API_URL,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            "Accept":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                supplierData
                            )
                    }
                );

        }


        // --------------------------------------------------
        // Read response
        // --------------------------------------------------

        const data =
            await response
                .json()
                .catch(() => ({}));


        // --------------------------------------------------
        // Handle backend error
        // --------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.message ||
                data.error ||
                (
                    isUpdate
                        ? "Unable to update supplier."
                        : "Unable to add supplier."
                )
            );

        }


        // --------------------------------------------------
        // Success
        // --------------------------------------------------

        showMessage(

            data.message ||

            (
                isUpdate
                    ? "Supplier updated successfully."
                    : "Supplier added successfully."
            ),

            "success"

        );


        // --------------------------------------------------
        // Clear form
        // --------------------------------------------------

        clearForm();


        // --------------------------------------------------
        // Reload supplier table
        // --------------------------------------------------

        await loadSuppliers();


    } catch (error) {

        console.error(
            "Supplier save error:",
            error
        );


        showMessage(
            error.message ||
            "Unable to save supplier.",
            "error"
        );

    }

}


// ==========================================================
// EDIT SUPPLIER
// ==========================================================

async function editSupplier(id) {

    if (!id) {

        showMessage(
            "Invalid supplier ID.",
            "error"
        );

        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/${encodeURIComponent(id)}`,
                {
                    method: "GET",

                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const data =
            await response
                .json()
                .catch(() => ({}));


        if (!response.ok) {

            throw new Error(
                data.message ||
                data.error ||
                "Unable to get supplier details."
            );

        }


        // Supports:
        //
        // { supplier_id: 1, ... }
        //
        // or:
        //
        // { supplier: {...} }

        const supplier =
            data.supplier ||
            data.data ||
            data;


        // --------------------------------------------------
        // Fill form
        // --------------------------------------------------

        if (supplierId) {

            supplierId.value =
                supplier.supplier_id ??
                id;

        }


        supplierName.value =
            supplier.supplier_name ??
            "";


        supplierEmail.value =
            supplier.supplier_email ??
            "";


        supplierProduct.value =
            supplier.product_name ??
            supplier.product_number ??
            "";


        minimumStock.value =
            supplier.minimum_stock ??
            "";


        // --------------------------------------------------
        // Change button text
        // --------------------------------------------------

        const submitButton =
            supplierForm.querySelector(
                'button[type="submit"]'
            );


        if (submitButton) {

            submitButton.textContent =
                "Update Supplier";

        }


        // --------------------------------------------------
        // Scroll to form
        // --------------------------------------------------

        supplierForm.scrollIntoView(
            {
                behavior:
                    "smooth",

                block:
                    "center"
            }
        );


    } catch (error) {

        console.error(
            "Error loading supplier:",
            error
        );


        showMessage(
            error.message ||
            "Unable to load supplier details.",
            "error"
        );

    }

}


// ==========================================================
// DELETE SUPPLIER
// ==========================================================

async function deleteSupplier(id) {

    if (!id) {

        showMessage(
            "Invalid supplier ID.",
            "error"
        );

        return;
    }


    const confirmed =
        confirm(
            "Are you sure you want to delete this supplier?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/${encodeURIComponent(id)}`,
                {
                    method:
                        "DELETE",

                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const data =
            await response
                .json()
                .catch(() => ({}));


        if (!response.ok) {

            throw new Error(
                data.message ||
                data.error ||
                "Unable to delete supplier."
            );

        }


        showMessage(
            data.message ||
            "Supplier deleted successfully.",
            "success"
        );


        clearForm();


        await loadSuppliers();


    } catch (error) {

        console.error(
            "Delete supplier error:",
            error
        );


        showMessage(
            error.message ||
            "Unable to delete supplier.",
            "error"
        );

    }

}


// ==========================================================
// CLEAR FORM
// ==========================================================

function clearForm() {

    if (!supplierForm) {
        return;
    }


    if (supplierId) {
        supplierId.value = "";
    }


    if (supplierName) {
        supplierName.value = "";
    }


    if (supplierEmail) {
        supplierEmail.value = "";
    }


    if (supplierProduct) {
        supplierProduct.value = "";
    }


    if (minimumStock) {
        minimumStock.value = "";
    }


    // ------------------------------------------------------
    // Reset button
    // ------------------------------------------------------

    const submitButton =
        supplierForm.querySelector(
            'button[type="submit"]'
        );


    if (submitButton) {

        submitButton.textContent =
            "Save Supplier";

    }


    if (supplierName) {

        supplierName.focus();

    }

}


// ==========================================================
// SEARCH SUPPLIERS
// ==========================================================

function filterSuppliers() {

    if (
        !searchInput ||
        !suppliersTableBody
    ) {

        return;
    }


    const searchValue =
        searchInput.value
            .toLowerCase()
            .trim();


    const rows =
        suppliersTableBody.querySelectorAll(
            "tr"
        );


    rows.forEach(
        row => {

            const text =
                row.textContent
                    .toLowerCase();


            row.style.display =
                text.includes(searchValue)
                    ? ""
                    : "none";

        }
    );

}


// ==========================================================
// ESCAPE HTML
// ==========================================================

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ==========================================================
// MESSAGE
// ==========================================================

function showMessage(
    message,
    type
) {

    // ------------------------------------------------------
    // Remove old message
    // ------------------------------------------------------

    const oldMessage =
        document.querySelector(
            ".stockflow-message"
        );


    if (oldMessage) {

        oldMessage.remove();

    }


    // ------------------------------------------------------
    // Create message
    // ------------------------------------------------------

    const messageBox =
        document.createElement(
            "div"
        );


    messageBox.className =
        `stockflow-message ${type}`;


    messageBox.textContent =
        message;


    document.body.appendChild(
        messageBox
    );


    // ------------------------------------------------------
    // Show
    // ------------------------------------------------------

    setTimeout(
        () => {

            messageBox.classList.add(
                "show"
            );

        },
        10
    );


    // ------------------------------------------------------
    // Remove
    // ------------------------------------------------------

    setTimeout(
        () => {

            messageBox.classList.remove(
                "show"
            );


            setTimeout(
                () => {

                    if (
                        messageBox.parentNode
                    ) {

                        messageBox.remove();

                    }

                },
                300
            );

        },
        3000
    );

}


// ==========================================================
// MAKE FUNCTIONS AVAILABLE GLOBALLY
// ==========================================================

window.editSupplier =
    editSupplier;


window.deleteSupplier =
    deleteSupplier;


window.loadSuppliers =
    loadSuppliers;


window.clearForm =
    clearForm;
