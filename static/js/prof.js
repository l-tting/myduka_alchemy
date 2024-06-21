function toggleDropdown() {
    const dropdown = document.querySelector('.dropdownn');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.profile') && !event.target.matches('.profile *')) {
        const dropdowns = document.querySelectorAll('.dropdownn');
        dropdowns.forEach(dropdown => {
            if (dropdown.style.display === 'block') {
                dropdown.style.display = 'none';
            }
        });
    }
}