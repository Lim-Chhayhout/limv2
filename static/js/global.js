/* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ */
/*                                - lim chhayhout [development] -                            */
/*                                          global script                                    */
/* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ */

const inputs = document.querySelectorAll('.lim-input-style');

inputs.forEach(input => {
    input.addEventListener('focus', function() {
        this.previousElementSibling.style.top = '-8px';
        this.previousElementSibling.style.fontSize = '0.75rem';
        this.previousElementSibling.style.zIndex = '11';
    });

    input.addEventListener('blur', function() {
        if (this.value.trim() === '') {
            this.previousElementSibling.style.top = '15px';
            this.previousElementSibling.style.fontSize = '0.9rem';
            this.previousElementSibling.style.zIndex = '9';
        }
    });

    if (input.value.trim() !== '') {
        input.previousElementSibling.style.top = '-8px';
        input.previousElementSibling.style.fontSize = '0.75rem';
        input.previousElementSibling.style.zIndex = '11';
    }
});