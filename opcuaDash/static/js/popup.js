document.addEventListener('DOMContentLoaded', function () {

    const modal = document.getElementById('welcomePopup');
    const span = document.getElementsByClassName('close')[0];
    const quoteText = document.getElementById('quoteText');

    async function loadRandomQuote() {
        try {

            const response = await fetch('/api/random-sentence');

            const data = await response.json();


            if (data && typeof data === 'object' && 'quote' in data) {
                quoteText.textContent = data.quote;
            } else {
                quoteText.textContent = 'Kein gültiges Zitat verfügbar.';
            }
        } catch (error) {
            console.error('Fehler beim Laden des Zitats:', error);
            quoteText.textContent = 'Ein kluger Gedanke begleitet dich durch den Tag.';
        }
    }


    modal.style.display = 'block';
    loadRandomQuote();

    span.onclick = function () {
        modal.style.display = 'none';
    }

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});