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
