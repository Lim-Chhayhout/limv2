/* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ */
/*                                - lim chhayhout [develop] -                                */
/*                                      handle admin js                                      */
/* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ */

(() => {
    const uploadBtn = document.querySelector('.upload');
    const imageUpload = document.getElementById('profile-upload');
    const previewImage = document.querySelector('.previewImage');

    if (uploadBtn && imageUpload && previewImage) {
        uploadBtn.addEventListener("click", function () {
            imageUpload.click();
        });

        imageUpload.addEventListener("change", function () {
            const file = this.files[0];
            if (!file) return;

            const allowedTypes = ['image/svg+xml', 'image/jpeg'];
            if (!allowedTypes.includes(file.type)) {
                alert("Only SVG, and JPG files are allowed.");
                this.value = "";
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                previewImage.src = event.target.result;
                previewImage.style.display = "block";
            };
            reader.readAsDataURL(file);
        });
    }
})();

(() => {
    const uploadBtn1 = document.querySelector('.upload1');
    const pimage1Upload = document.getElementById('pimage1-upload');
    const previewImage1 = document.querySelector('.previewImage1');

    if (uploadBtn1 && pimage1Upload && previewImage1) {
        uploadBtn1.addEventListener("click", function () {
            pimage1Upload.click();
        });

        pimage1Upload.addEventListener("change", function () {
            const file1 = this.files[0];
            if (!file1) return;

            const allowedTypes = ['image/svg+xml', 'image/jpeg'];
            if (!allowedTypes.includes(file1.type)) {
                alert("Only SVG, and JPG files are allowed.");
                this.value = "";
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                previewImage1.src = event.target.result;
                previewImage1.style.display = "block";
            };
            reader.readAsDataURL(file1);
        });
    }
})();
(() => {
    const uploadBtn2 = document.querySelector('.upload2');
    const pimage2Upload = document.getElementById('pimage2-upload');
    const previewImage2 = document.querySelector('.previewImage2');

    if (uploadBtn2 && pimage2Upload && previewImage2) {
        uploadBtn2.addEventListener("click", function () {
            pimage2Upload.click();
        });

        pimage2Upload.addEventListener("change", function () {
            const file2 = this.files[0];
            if (!file2) return;

            const allowedTypes = ['image/svg+xml', 'image/jpeg'];
            if (!allowedTypes.includes(file2.type)) {
                alert("Only SVG, and JPG files are allowed.");
                this.value = "";
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                previewImage2.src = event.target.result;
                previewImage2.style.display = "block";
            };
            reader.readAsDataURL(file2);
        });
    }
})();

(() => {
    document.querySelectorAll('tr.row[data-href]').forEach(row => {
        row.addEventListener('dblclick', e => {
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
            if (statusSelect.value === "false") {
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

    setupStockToggle('pstatus-add', 'stock-add', 'row-add-stock');
    setupStockToggle('pstatus-edit', 'stock-edit', 'row-edit-stock');
})();

