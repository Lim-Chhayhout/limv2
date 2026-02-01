(() => {
   const initFormHandler = (selector, redirectPattern = null) => {
        const form = document.querySelector(selector);
        const report = document.querySelector(".system-report");
        if (!form || !report) return;

        const showMessage = (type, msg) => {
            report.style.display = "flex";
            const boxes = report.querySelectorAll(".box");
            boxes.forEach(box => box.style.display = "none");
            const box = report.querySelector(`.${type}`);
            if (box) {
                box.querySelector(".message").textContent = msg;
                box.style.display = "flex";
            }
            setTimeout(() => {
                report.style.display = "none";
            }, 4000);
        };

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const actionUrl = form.dataset.action || form.action || window.location.href;
            const formData = new FormData(form);

            try {
                const res = await fetch(actionUrl, { method: "POST", body: formData });
                const data = await res.json();

                if (res.ok && data.success) {
                    showMessage("success", data.success);
                    setTimeout(() => {
                        if (redirectPattern) {
                            let redirectUrl = redirectPattern;

                            if (data.user_id) {
                                redirectUrl = redirectUrl.replace("${userId}", data.user_id);
                            } else if (data.category_id) {
                                redirectUrl = redirectUrl.replace("${categoryId}", data.category_id);
                            } else if (data.product_id) {
                                redirectUrl = redirectUrl.replace("${productId}", data.product_id);
                            }else if (data.sale_id) {
                                redirectUrl = redirectUrl.replace("${saleId}", data.sale_id);
                            }else if (data.order_id) {
                                redirectUrl = redirectUrl.replace("${orderId}", data.order_id);
                            }

                            window.location.href = redirectUrl;
                        }
                    }, 1500);
                } else if (data.error) {
                    showMessage("error", data.error);
                } else if (data.warning) {
                    showMessage("warning", data.warning);
                }
            } catch {
                showMessage("error", "Network error or server issue.");
            }
        });
    };

   initFormHandler("#user-form", "/user-management/show-user/${userId}");
   initFormHandler("#product-form", "/product-management/show-product/${productId}");
   initFormHandler("#sale-form", "/sale-management/show-sale/${saleId}");
   initFormHandler("#add-sale", "/sale-management/show-sale/${orderId}");
   initFormHandler("#category-form", "/category-management");

})();

(() => {
    document.querySelectorAll(".image-input").forEach(container => {
        const uploadBtn = container.querySelector(".upload");
        const imageUpload = container.querySelector("input[type='file']");
        const previewImage = container.querySelector(".pre-image");
        const report = document.querySelector(".system-report");

        if (!uploadBtn || !imageUpload || !previewImage || !report) return;

        const showMessage = (type, msg) => {
            report.style.display = "flex";
            const boxes = report.querySelectorAll(".box");
            boxes.forEach(box => box.style.display = "none");
            const box = report.querySelector(`.${type}`);
            if (box) {
                box.querySelector(".message").textContent = msg;
                box.style.display = "flex";
            }
            setTimeout(() => {
                report.style.display = "none";
            }, 4000);
        };

        uploadBtn.addEventListener("click", () => imageUpload.click());

        imageUpload.addEventListener("change", () => {
            const file = imageUpload.files[0];
            if (!file) return;

            const allowedTypes = ["image/jpeg", "image/png", "image/svg+xml"];
            if (!allowedTypes.includes(file.type)) {
                showMessage("warning", "Only SVG, PNG and JPG files are allowed.");
                imageUpload.value = "";
                return;
            }

            const reader = new FileReader();
            reader.onload = e => {
                previewImage.src = e.target.result;
                previewImage.style.display = "block";
            };
            reader.readAsDataURL(file);
        });
    });
})();

(() => {
    const report = document.querySelector(".system-report");
    const deleteLinks = document.querySelectorAll(".delete-link");

    if (!deleteLinks.length || !report) return;

    const showMessage = (type, msg) => {
        report.style.display = "flex";
        const boxes = report.querySelectorAll(".box");
        boxes.forEach(b => b.style.display = "none");

        const box = report.querySelector(`.${type}`);
        if (box) {
            box.querySelector(".message").textContent = msg;
            box.style.display = "flex";
        }

        setTimeout(() => report.style.display = "none", 4000);
    };

    deleteLinks.forEach(link => {
        link.addEventListener("click", async e => {
            e.preventDefault();

            const url = link.getAttribute("href");
            const redirect = link.dataset.redirect || window.location.href;
            const type = link.dataset.type;
            const id = link.dataset.id;

            if (!confirm(`Delete this ${type} (ID ${id})?`)) return;

            try {
                const res = await fetch(url, { method: "POST" });
                const data = await res.json();

                if (res.ok && data.success) {
                    showMessage("success", data.success);
                    setTimeout(() => (window.location.href = redirect), 1500);
                } else if (data.error) {
                    showMessage("error", data.error);
                } else if (data.warning) {
                    showMessage("warning", data.warning);
                }
            } catch {
                showMessage("error", "Network error or server issue.");
            }
        });
    });
})();

(() => {
    const rows = document.querySelectorAll('tr.row[data-href]');

    rows.forEach(row => {
        row.addEventListener('click', e => {
            if (e.target.closest('button') || e.target.closest('a')) return;
            window.location.href = row.dataset.href;
        });
    });
})();

(() => {
    const setupStockToggle = (statusId, stockId, rowId) => {
        const statusSelect = document.getElementById(statusId);
        const stockInput = document.getElementById(stockId);
        const rowStock = document.getElementById(rowId);

        if (!statusSelect || !stockInput || !rowStock) return;

        const toggleStock = () => {
            if (statusSelect.value === "Pre-order") {
                rowStock.style.display = "none";
                stockInput.disabled = true;
                stockInput.value = "0";
            } else {
                rowStock.style.display = "flex";
                stockInput.disabled = false;
                stockInput.value = "";
            }
        };

        toggleStock();
        statusSelect.addEventListener('change', toggleStock);
    };

    setupStockToggle('status-add', 'stock-add', 'row-add-stock');
    setupStockToggle('status-edit', 'stock-edit', 'row-edit-stock');
})();

(() => {
    const userTableBody = document.querySelector('.tbl-user');
    const userSearchInput = document.querySelector('input[name="search-user"]');
    if (userTableBody && userSearchInput) {
        const userRows = Array.from(userTableBody.querySelectorAll('tr.row'));
        const roleOrder = { "Super Admin": 1, "Admin": 2, "Employee": 3 };

        userSearchInput.addEventListener('input', () => {
            const query = userSearchInput.value.toLowerCase().trim();
            const filtered = userRows
                .map(row => {
                    const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                    const role = row.querySelector('.role-user')?.textContent || '';
                    const matchScore = name.startsWith(query) ? 1 : name.includes(query) ? 2 : 99;
                    return { row, matchScore, roleScore: roleOrder[role] || 99 };
                })
                .filter(item => item.matchScore < 99)
                .sort((a, b) => a.matchScore - b.matchScore || a.roleScore - b.roleScore)
                .map(item => item.row);

            userRows.forEach(r => r.style.display = 'none');
            filtered.forEach(r => r.style.display = 'table-row');

            let noData = userTableBody.querySelector('.null-data');
            if (!filtered.length) {
                if (!noData) {
                    noData = document.createElement('tr');
                    noData.classList.add('row', 'null-data');
                    noData.innerHTML = `<td class="pd-l" colspan="5">No user found!</td>`;
                    userTableBody.appendChild(noData);
                }
                noData.style.display = 'table-row';
            } else if (noData) {
                noData.style.display = 'none';
            }
        });
    }

    const categoryTableBody = document.querySelector('.tbl-category');
    const categorySearchInput = document.querySelector('input[name="search-category"]');
    if (categoryTableBody && categorySearchInput) {
        const categoryRows = Array.from(categoryTableBody.querySelectorAll('tr.row'));

        categorySearchInput.addEventListener('input', () => {
            const query = categorySearchInput.value.toLowerCase().trim();
            const filtered = categoryRows
                .filter(row => {
                    const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
                    const desc = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                    return name.includes(query) || desc.includes(query);
                });

            categoryRows.forEach(r => r.style.display = 'none');
            filtered.forEach(r => r.style.display = 'table-row');

            let noData = categoryTableBody.querySelector('.null-data');
            if (!filtered.length) {
                if (!noData) {
                    noData = document.createElement('tr');
                    noData.classList.add('row', 'null-data');
                    noData.innerHTML = `<td class="pd-l" colspan="3">No category found!</td>`;
                    categoryTableBody.appendChild(noData);
                }
                noData.style.display = 'table-row';
            } else if (noData) {
                noData.style.display = 'none';
            }
        });
    }

    const productTableBody = document.querySelector('.tbl-product');
    const productSearchInput = document.querySelector('input[name="search-product"]');

    if (productTableBody && productSearchInput) {
        const productRows = Array.from(productTableBody.querySelectorAll('tr.row'));

        productSearchInput.addEventListener('input', () => {
            const query = productSearchInput.value.toLowerCase().trim();
            const filtered = productRows.filter(row => {
                const code = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                return code.includes(query);
            });

            productRows.forEach(r => r.style.display = 'none');
            filtered.forEach(r => r.style.display = 'table-row');

            let noData = productTableBody.querySelector('.null-data');
            if (!filtered.length) {
                if (!noData) {
                    noData = document.createElement('tr');
                    noData.classList.add('row', 'null-data');
                    noData.innerHTML = `<td class="pd-l" colspan="5">No product found!</td>`;
                    productTableBody.appendChild(noData);
                }
                noData.style.display = 'table-row';
            } else if (noData) {
                noData.style.display = 'none';
            }
        });
    }

    const saleTableBody = document.querySelector('.tbl-sale');
    const saleSearchInput = document.querySelector('input[name="search-sale"]');

    if (saleTableBody && saleSearchInput) {
        const saleRows = Array.from(saleTableBody.querySelectorAll('tr.row'));

        saleSearchInput.addEventListener('input', () => {
            const query = saleSearchInput.value.toLowerCase().trim();

            const filtered = saleRows.filter(row => {
                const orderNumberCell = row.querySelector('td:nth-child(1)');
                const customerCell = row.querySelector('td:nth-child(3)');

                const orderNumber = orderNumberCell ? orderNumberCell.textContent.toLowerCase() : '';
                const customerName = customerCell ? customerCell.textContent.toLowerCase() : '';

                return orderNumber.includes(query) || customerName.includes(query);
            });

            saleRows.forEach(r => r.style.display = 'none');
            filtered.forEach(r => r.style.display = 'table-row');

            let noData = saleTableBody.querySelector('.null-data');
            if (!filtered.length) {
                if (!noData) {
                    noData = document.createElement('tr');
                    noData.classList.add('row', 'null-data');
                    noData.innerHTML = `<td class="pd-l" colspan="6">No sale found!</td>`;
                    saleTableBody.appendChild(noData);
                }
                noData.style.display = 'table-row';
            } else if (noData) {
                noData.style.display = 'none';
            }
        });
    }

    const searchInput = document.querySelector('input[name="search-sale-product"]');
    const cards = Array.from(document.querySelectorAll('.list-sale-products .card'));

    if (searchInput && cards.length) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.toLowerCase().trim();
            let visibleCount = 0;

            cards.forEach(card => {
                const code = card.querySelector('.product-code')?.textContent.toLowerCase() || '';
                const name = card.querySelector('.product-name')?.textContent.toLowerCase() || '';

                const match = code.includes(query) || name.includes(query);
                card.style.display = match ? '' : 'none';
                if (match) visibleCount++;
            });

            let noData = document.querySelector('.no-product');
            if (!visibleCount) {
                if (!noData) {
                    noData = document.createElement('div');
                    noData.className = 'no-product';
                    noData.textContent = 'No product found!';
                    document.querySelector('.list-sale-products').appendChild(noData);
                }
                noData.style.display = 'block';
            } else if (noData) {
                noData.style.display = 'none';
            }
        });
    }

    document.addEventListener("DOMContentLoaded", () => {

        const selectedContainer = document.getElementById("selected-products");
        const saveBtn = document.getElementById("btn-save-selected");

        if (selectedContainer && saveBtn) {
            const savedCodes = JSON.parse(selectedContainer.dataset.selected || "[]");
            let tempSelected = [...savedCodes];

            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                const btn = card.querySelector('.checkbox button');
                const code = card.dataset.code;
                if (!btn || !code) return;

                if (tempSelected.includes(code)) {
                    card.classList.add('selected');
                    btn.innerHTML = '<i class="fi fi-rr-check"></i>';
                }

                card.addEventListener('click', () => {
                    card.classList.toggle('selected');
                    if (card.classList.contains('selected')) {
                        if (!tempSelected.includes(code)) tempSelected.push(code);
                        btn.innerHTML = '<i class="fi fi-rr-check"></i>';
                    } else {
                        tempSelected = tempSelected.filter(c => c !== code);
                        btn.innerHTML = '';
                    }
                });
            });

            saveBtn.addEventListener("click", () => {
                fetch('/sale-management/save-selected-products', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({selected_codes: tempSelected})
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        window.location.href = data.redirect_url;
                    }
                });
            });
        }
    });
})();

(() => {
    const pqBoxes = document.querySelectorAll(".pq");
    const removeBtns = document.querySelectorAll(".selected-list .remove");
    const shippingSelect = document.getElementById("shipping-select");
    const shippingCostInput = document.getElementById("shipping-cost");

    if (pqBoxes.length === 0 && removeBtns.length === 0 && !shippingSelect) return;

    function updateButtons(box, qty, max) {
        const minus = box.querySelector(".d-qty");
        const plus = box.querySelector(".i-qty");
        if (!minus || !plus) return;

        minus.style.pointerEvents = qty <= 1 ? "none" : "auto";
        minus.style.opacity = qty <= 1 ? "0.3" : "1";

        plus.style.pointerEvents = qty >= max ? "none" : "auto";
        plus.style.opacity = qty >= max ? "0.3" : "1";
    }

    function updateSubPrice(row) {
        const qtyInput = row.querySelector(".pq input");
        if (!qtyInput) return;

        const price = parseFloat(qtyInput.dataset.price) || 0;
        const qty = parseInt(qtyInput.value) || 0;

        const subInput = row.querySelector(".sub-price input");
        if (subInput) subInput.value = "$" + (qty * price).toFixed(2);
    }

    function updateTotals() {
        let totalQty = 0;
        let subtotal = 0;

        pqBoxes.forEach(box => {
            const input = box.querySelector("input");
            if (!input) return;
            const qty = parseInt(input.value) || 0;
            const price = parseFloat(input.dataset.price) || 0;
            totalQty += qty;
            subtotal += qty * price;
        });

        const shippingCost = shippingCostInput ? parseFloat(shippingCostInput.value) || 0 : 0;
        const totalAmount = subtotal + shippingCost;

        const itemCount = document.querySelector(".head-sale .summary .item");
        if (itemCount) itemCount.textContent = "x" + totalQty;

        const totalPrice = document.querySelector(".head-sale .summary .total");
        if (totalPrice) totalPrice.textContent = "$" + totalAmount.toFixed(2);
    }

    // Handle shipping change
    if (shippingSelect && shippingCostInput) {
        shippingSelect.addEventListener("change", () => {
            const selectedOption = shippingSelect.selectedOptions[0];
            shippingCostInput.value = parseFloat(selectedOption.dataset.cost) || 0;
            updateTotals();
        });
    }

    // Handle quantity buttons
    pqBoxes.forEach(box => {
        const input = box.querySelector("input");
        if (!input) return;

        const code = input.dataset.pcode;
        let qty = parseInt(input.value) || 1;
        let status = input.dataset.status;
        let stock = parseInt(input.dataset.stock) || 0;
        let max = status === "Pre-order" ? 10 : stock;

        updateButtons(box, qty, max);
        updateSubPrice(box.closest(".row"));

        const minusBtn = box.querySelector(".d-qty");
        const plusBtn = box.querySelector(".i-qty");

        if (minusBtn) minusBtn.onclick = () => {
            fetch(`/sale-management/update-product-qty/${code}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action: "decrease" })
            })
            .then(r => r.json())
            .then(d => {
                qty = d.qty;
                status = d.product_status;
                stock = d.stock;
                max = status === "Pre-order" ? 10 : stock;

                input.value = qty;
                updateButtons(box, qty, max);
                updateSubPrice(box.closest(".row"));
                updateTotals();
            });
        };

        if (plusBtn) plusBtn.onclick = () => {
            fetch(`/sale-management/update-product-qty/${code}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action: "increase" })
            })
            .then(r => r.json())
            .then(d => {
                qty = d.qty;
                status = d.product_status;
                stock = d.stock;
                max = status === "Pre-order" ? 10 : stock;

                input.value = qty;
                updateButtons(box, qty, max);
                updateSubPrice(box.closest(".row"));
                updateTotals();
            });
        };
    });

    // Handle remove buttons
    removeBtns.forEach(btn => {
        btn.onclick = e => {
            e.preventDefault();
            const code = btn.dataset.code;
            const row = btn.closest(".row");
            if (!code || !row) return;

            fetch(`/sale-management/remove-product/${code}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            })
            .then(r => r.json())
            .then(d => {
                if (d.status === "success") {
                    row.remove();
                    updateTotals();
                }
            });
        };
    });

    // Initial calculation
    updateTotals();
})();

(() => {
    const shippingSelect = document.getElementById("shipping-select");
    const shippingCostInput = document.getElementById("shipping-cost");
    const totalAmountEl = document.getElementById("total-amount");

    if (!shippingCostInput || !totalAmountEl) return;

    function updateTotal() {
        let subtotal = 0;

        document.querySelectorAll(".product-subtotal").forEach(el => {
            const price = Number(el.dataset.price) || 0;
            const qty = Number(el.dataset.qty) || 0;
            subtotal += price * qty;
        });

        const shippingCost = Number(shippingCostInput.value) || 0;
        totalAmountEl.textContent = "$" + (subtotal + shippingCost).toFixed(2);
    }

    if (shippingSelect) {
        shippingSelect.addEventListener("change", () => {
            const option = shippingSelect.selectedOptions[0];
            shippingCostInput.value = Number(option?.dataset.cost) || 0;
            updateTotal();
        });
    }

    updateTotal();
})();



