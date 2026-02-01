(() => {
    const subProductImages = document.querySelectorAll('.detail .sub-slide .slide img');
    const mainProductImage = document.getElementById('display-image');
    const bdOverSubImage = document.querySelectorAll('.detail .sub-slide .slide');

    if (!subProductImages.length || !mainProductImage || !bdOverSubImage.length) return;

    const setActiveImage = index => {
        mainProductImage.src = subProductImages[index].src;
        bdOverSubImage.forEach((img, i) => {
            img.style.border = i === index ? '1px solid #000000' : '1px solid rgba(0, 0, 0, 0.2)';
        });
    };

    setActiveImage(0);

    subProductImages.forEach((subImage, index) => {
        ['mouseover', 'touchstart', 'click'].forEach(evt =>
            subImage.addEventListener(evt, () => setActiveImage(index))
        );
    });
})();

(() => {
    const cityDropdown = document.getElementById("city-dropdown");
    const districtDropdown = document.getElementById("district-dropdown");

    if (!cityDropdown || !districtDropdown) return;

    const cities = {
        "Phnom Penh": ["Khan Chamkar Mon", "Khan Daun Penh", "Khan Toul Kork", "Khan Sen Sok"],
        "Battambang": ["Battambang Municipality", "Banan", "Thma Koul", "Phnum Proek"],
        "Siem Reap": ["Siem Reap Municipality", "Angkor Chum", "Svay Dangkum"]
    };

    const selectedCity = document.getElementById("selected-city");
    const hiddenCityInput = document.getElementById("hidden-city-selected");
    const cityBox = document.getElementById("city-box");
    const spanCity = document.getElementById("span-holder-city");

    const selectedDistrict = document.getElementById("selected-district");
    const hiddenDistrictInput = document.getElementById("hidden-district-selected");
    const districtBox = document.getElementById("district-box");
    const spanDistrict = document.getElementById("span-holder-dis");

    const toggleDropdown = dropdown => {
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    };

    const populateDropdown = (dropdown, items, onSelect, span) => {
        dropdown.innerHTML = "";
        if (!items.length) {
            const div = document.createElement("div");
            div.textContent = "No City Selected";
            div.style.color = "#838383";
            div.style.cursor = "not-allowed";
            dropdown.appendChild(div);
            return;
        }
        items.forEach(item => {
            const div = document.createElement("div");
            div.textContent = item;
            div.addEventListener("click", () => {
                onSelect(item);
                dropdown.style.display = "none";
                span.style.top = "-8px";
                span.style.fontSize = "0.75rem";
                span.style.zIndex = "11";
            });
            dropdown.appendChild(div);
        });
    };

    const selectCity = city => {
        selectedCity.textContent = city;
        hiddenCityInput.value = city;
        spanCity.style.top = "-8px";
        spanCity.style.fontSize = "0.75rem";
        spanCity.style.zIndex = "11";

        selectedDistrict.textContent = "";
        hiddenDistrictInput.value = "";
        spanDistrict.style.top = "15px";
        spanDistrict.style.fontSize = "0.9rem";
        spanDistrict.style.zIndex = "9";

        populateDropdown(districtDropdown, cities[city] || [], selectDistrict, spanDistrict);

        const shippingType = document.getElementById("delivery-type");
        const shippingCost = document.getElementById("delivery-cost");
        const total = document.getElementById("total");

        if (!shippingType || !total || !shippingCost) return;

        const shippingId = city === "Phnom Penh" ? 1 : 2;

        fetch(`/shipping/${shippingId}`, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                shippingType.textContent = data.shipping_type;
                shippingCost.textContent = parseFloat(data.shipping_cost).toFixed(2);
                total.textContent = parseFloat(data.total).toFixed(2);
            }
        });

    };

    const selectDistrict = district => {
        selectedDistrict.textContent = district;
        hiddenDistrictInput.value = district;
        spanDistrict.style.top = "-8px";
        spanDistrict.style.fontSize = "0.75rem";
        spanDistrict.style.zIndex = "11";
    };

    populateDropdown(cityDropdown, Object.keys(cities), selectCity, spanCity);

    cityBox.addEventListener("click", e => {
        e.stopPropagation();
        toggleDropdown(cityDropdown);
    });

    districtBox.addEventListener("click", e => {
        e.stopPropagation();
        if (!hiddenCityInput.value) populateDropdown(districtDropdown, []);
        toggleDropdown(districtDropdown);
    });

    document.addEventListener("click", () => {
        cityDropdown.style.display = "none";
        districtDropdown.style.display = "none";
    });
})();

(() => {

    function updateButtons(box, qty, max) {
        const minus = box.querySelector(".d-qty");
        const plus = box.querySelector(".i-qty");

        minus.style.pointerEvents = qty <= 1 ? "none" : "auto";
        minus.style.opacity = qty <= 1 ? "0.3" : "1";

        plus.style.pointerEvents = qty >= max ? "none" : "auto";
        plus.style.opacity = qty >= max ? "0.3" : "1";
    }

    function updateTotals() {
        let totalQty = 0;
        let subtotal = 0;

        document.querySelectorAll('.pq input').forEach(input => {
            const qty = parseInt(input.value);
            const price = parseFloat(input.dataset.price);

            totalQty += qty;
            subtotal += qty * price;
        });

        const totalQtyEl = document.querySelector(".head span");
        if (totalQtyEl) totalQtyEl.textContent = totalQty;

        const itemCount = document.querySelector(".cal .row:nth-child(1) div:last-child");
        if (itemCount) itemCount.textContent = "x" + totalQty;

        const subtotalEl = document.querySelector(".subtotal div:last-child");
        if (subtotalEl) subtotalEl.textContent = "$" + subtotal.toFixed(2);
    }

    document.querySelectorAll(".pq").forEach(box => {
        const input = box.querySelector("input");
        const id = input.dataset.pid;
        const status = input.dataset.status;
        const stock = parseInt(input.dataset.stock);

        const minus = box.querySelector(".d-qty");
        const plus = box.querySelector(".i-qty");

        let max = status === "Pre-order" ? 10 : stock;

        updateButtons(box, parseInt(input.value), max);

        minus.onclick = () => {
            fetch(`/api/cart/dec/${id}`)
                .then(r => r.json())
                .then(d => {
                    input.value = d.qty;
                    updateButtons(box, d.qty, max);
                    updateTotals();
                });
        };

        plus.onclick = () => {
            fetch(`/api/cart/inc/${id}`)
                .then(r => r.json())
                .then(d => {
                    max = d.status === "Pre-order" ? 10 : d.stock;
                    input.value = d.qty;
                    updateButtons(box, d.qty, max);
                    updateTotals();
                });
        };
    });

})();


(() => {
    const form = document.getElementById("checkout-form");
    if (!form) return;

    const contactBox = document.getElementById("error-contact");
    const contactText = contactBox ? contactBox.querySelector("span") : null;

    const addressBox = document.getElementById("error-address");
    const addressText = addressBox ? addressBox.querySelector("span") : null;

    const spanCity = document.getElementById("span-holder-city");
    const spanDis = document.getElementById("span-holder-dis");
    const spanAddress = document.getElementById("span-holder-address");

    if (!contactBox || !contactText || !addressBox || !addressText || !spanCity || !spanDis) return;

    const contactFields = [
        { id: "email", label: "Please enter your email!" },
        { id: "phone", label: "Please enter your phone number!" },
        { id: "name",  label: "Please enter your name!" }
    ];

    const addressFields = [
        { id: "hidden-city-selected",     type: "select",  label: "Please select your city!" },
        { id: "hidden-district-selected", type: "select",  label: "Please select your district!" },
        { id: "address",                  type: "input",   label: "Please enter your address!" }
    ];

    form.addEventListener("submit", e => {
        let contactValid = true;
        let addressValid = true;

        contactBox.style.display = "none";
        contactText.textContent = "";

        addressBox.style.display = "none";
        addressText.textContent = "";

        contactFields.forEach(f => {
            const input = document.getElementById(f.id);
            if (!input) return;

            const span = input.previousElementSibling;

            if (!input.value.trim()) {
                input.classList.add("empty-input");
                if (span) span.classList.add("empty-span");

                if (contactValid) {
                    contactText.textContent = f.label;
                    contactBox.style.display = "flex";
                }

                contactValid = false;
            } else {
                input.classList.remove("empty-input");
                if (span) span.classList.remove("empty-span");
            }
        });

        addressFields.forEach(f => {
            const el = document.getElementById(f.id);
            if (!el) return;

            let isEmpty = !el.value.trim();
            let box = f.type === "select" ? el.closest(".lim-selection-box") : el;

            if (isEmpty) {
                if (f.type !== "select") box.classList.add("empty-input");
                else if (box) box.style.border = "1px solid #ff0000";

                if (addressValid) {
                    addressText.textContent = f.label;
                    addressBox.style.display = "flex";
                }

                spanCity.style.color = !document.getElementById("hidden-city-selected")?.value.trim() ? "#ff0000" : "#000000";
                spanDis.style.color = !document.getElementById("hidden-district-selected")?.value.trim() ? "#ff0000" : "#000000";
                spanAddress.style.color = !document.getElementById("address")?.value.trim() ? "#ff0000" : "#ff0000";

                addressValid = false;
            } else {
                if (f.type !== "select") box.classList.remove("empty-input");
                else if (box) box.style.border = "1px solid #00000050";

                spanCity.style.color = "#000000";
                spanDis.style.color = "#000000";
                spanAddress.style.color = "#000000";
            }
        });

        if (!contactValid || !addressValid) e.preventDefault();
    });
})();

(() => {
    const options = document.querySelectorAll(".option-con-payment");
    const paymentInput = document.getElementById("payment-method");
    const form = document.getElementById("checkout-form");
    const errorBox = document.getElementById("error-payment");

    if (!options.length || !paymentInput || !form || !errorBox) return;

    const errorText = errorBox.querySelector("span");
    if (!errorText) return;

    options.forEach(option => {
        option.addEventListener("click", () => {
            options.forEach(opt => {
                opt.classList.remove("selected");
                const title = opt.querySelector(".title");
                if (title) title.style.color = "#00000060";
            });

            option.classList.add("selected");
            const title = option.querySelector(".title");
            if (title) title.style.color = "#000000";

            paymentInput.value = option.dataset.value;

            errorBox.style.display = "none";
            errorText.textContent = "";
        });
    });

    form.addEventListener("submit", e => {
        if (!paymentInput.value.trim()) {
            errorText.textContent = "Please select a payment method!";
            errorBox.style.display = "flex";

            options.forEach(opt => {
                opt.style.border = "1px solid #ff0000";
            });

            e.preventDefault();
        } else {
            options.forEach(opt => {
                opt.style.border = "";
            });
        }
    });
})();

(() => {
    const button = document.getElementById("download");
    const element = document.querySelector(".invoice");

    if (!button || !element) return;

    button.addEventListener("click", () => {
        button.style.display = "none";

        const options = {
            margin: 0.2,
            filename: 'Lim_invoice.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
        };

        html2pdf().set(options).from(element).save()
            .then(() => button.style.display = "block")
            .catch(err => {
                console.error("Error generating PDF:", err);
                button.style.display = "block";
            });
    });
})();










