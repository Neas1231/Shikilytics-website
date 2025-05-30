document.getElementById('toggleButton').addEventListener('click', function() {
    const hiddenElement = document.getElementById('profile');
    if (hiddenElement.style.display === "none" || hiddenElement.style.display === "") {
        hiddenElement.style.display = "block";
    } else {
        hiddenElement.style.display = ""; 
    }
});