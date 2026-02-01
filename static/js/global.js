(() => {
    const inputs = document.querySelectorAll('.lim-input-style');
    if (inputs.length === 0) return; // nothing to do

    inputs.forEach((input) => {
        const label = input.previousElementSibling;
        if (!label) return;

        input.addEventListener('focus', () => {
            label.style.top = '-8px';
            label.style.fontSize = '0.75rem';
            label.style.zIndex = '11';
        });

        input.addEventListener('blur', () => {
            if (input.value.trim() === '') {
                label.style.top = '15px';
                label.style.fontSize = '0.9rem';
                label.style.zIndex = '9';
            }
        });

        if (input.value.trim() !== '') {
            label.style.top = '-8px';
            label.style.fontSize = '0.75rem';
            label.style.zIndex = '11';
        }
    });
})();

(() => {
    const slider = document.querySelector('.global-slider .slider');
    if (!slider) return;

    const slides = slider.querySelectorAll('.slide');
    const dots = slider.querySelectorAll('.pointer .p');

    let index = 0;
    let direction = 1;

    const showSlide = i => {
        slides.forEach((s, n) => {
            s.style.transform = `translateX(${(n - i) * 100}%)`;
        });
        dots.forEach((d, n) => {
            d.classList.toggle('active', n === i);
        });
    };

    showSlide(index);

    setInterval(() => {
        index += direction;

        if (index === slides.length - 1) direction = -1;
        else if (index === 0) direction = 1;

        showSlide(index);
    }, 10000);
})();

(() => {
    const root = document.querySelector('.global-option');
    if (!root) return;

    const btn = root.querySelector('.search-bar');
    const panel = root.querySelector('.search');
    const input = panel.querySelector('input');

    let open = false;

    const closeSearch = () => {
        open = false;
        panel.classList.remove('active');
    };

    btn.addEventListener('click', e => {
        e.stopPropagation();
        open = !open;
        panel.classList.toggle('active', open);

        if (open) {
            setTimeout(() => {
                input.focus();
            }, 200);
        }
    });

    document.addEventListener('click', e => {
        if (!panel.contains(e.target) && !btn.contains(e.target)) {
            closeSearch();
        }
    });

    window.addEventListener('scroll', () => {
        if (!open) return;
        closeSearch();
    });
})();

(() => {
    const root = document.querySelector('.global-option');
    if (!root) return;

    const btn = root.querySelector('.filter-bar');
    const panel = root.querySelector('.filter');

    let open = false;

    const closeFilter = () => {
        open = false;
        panel.classList.remove('active');
    };

    btn.addEventListener('click', e => {
        e.stopPropagation();
        open = !open;
        panel.classList.toggle('active', open);

    });

    document.addEventListener('click', e => {
        if (!panel.contains(e.target) && !btn.contains(e.target)) {
            closeFilter();
        }
    });

    window.addEventListener('scroll', () => {
        if (!open) return;
        closeFilter();
    });
})();

(() => {
    const root = document.querySelector('.global-option');
    if (!root) return;

    const btn = root.querySelector('.nav-bar');
    const panel = root.querySelector('.nav');

    let open = false;

    const closeNav = () => {
        open = false;
        panel.classList.remove('active');
    };

    btn.addEventListener('click', e => {
        e.stopPropagation();
        open = !open;
        panel.classList.toggle('active', open);

    });

    document.addEventListener('click', e => {
        if (!panel.contains(e.target) && !btn.contains(e.target)) {
            closeNav();
        }
    });

    window.addEventListener('scroll', () => {
        if (!open) return;
        closeNav();
    });
})();

(() => {
    const searchInput = document.querySelector('.search-input');
    const suggestList = document.querySelector('.suggest-list');
    const suggestBox = document.querySelector('.suggest-search');
    const quickBox = document.querySelector('.quick-search');
    const quickList = document.querySelector('.quick-list');

    if (!searchInput || !suggestList || !suggestBox || !quickBox || !quickList) return;

    let lastResults = [];

    fetch("/quick-search")
        .then(res => res.json())
        .then(data => {
            quickList.innerHTML = "";
            data.forEach(item => {
                quickList.innerHTML += `
                    <a class="flex" href="/product-detail/${item.id}">
                        <i class="fi fi-rr-angle-small-right"></i>
                        <span>${item.code}</span>
                    </a>
                `;
            });
        });

    searchInput.addEventListener("keyup", function(e) {
        const key = this.value.trim();

        if (key === "") {
            suggestBox.style.display = "none";
            quickBox.style.display = "flex";
            suggestList.innerHTML = "";
            lastResults = [];
            return;
        }

        if (e.key === "Enter") {
            e.preventDefault();
            if (lastResults.length > 0) {
                window.location.href = `/product-detail/${lastResults[0].id}`;
            }
            return;
        }

        fetch(`/search-product?key=${key}`)
            .then(res => res.json())
            .then(data => {
                lastResults = data;
                suggestList.innerHTML = "";

                if (data.length === 0) {
                    suggestBox.style.display = "none";
                    quickBox.style.display = "flex";
                    return;
                }

                suggestBox.style.display = "flex";
                quickBox.style.display = "none";

                data.forEach(item => {
                    suggestList.innerHTML += `
                        <a class="flex" href="/product-detail/${item.id}">
                            <i class="fi fi-rr-angle-small-right"></i>
                            <span>${item.code}</span>
                        </a>
                    `;
                });
            });
    });
})();

(() => {

    document.addEventListener("DOMContentLoaded", () => {

        const form = document.querySelector("form[action='/login-post']");
        if (!form) return;

        const errorBox = document.getElementById("error-login");
        const errorMessage = document.getElementById("error-message");

        if (errorBox) errorBox.style.display = "none";

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(form);

            try {
                const res = await fetch("/login-post", {
                    method: "POST",
                    body: formData,
                });

                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                const data = await res.json();
                if (data.error) showError(data.error);

            } catch (err) {
                showError("Something went wrong.");
            }
        });

        function showError(message) {
            if (!errorBox || !errorMessage) return;
            errorMessage.textContent = message;
            errorBox.style.display = "flex";
        }
    });

})();