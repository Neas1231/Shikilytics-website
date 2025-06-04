const help = document.querySelector(".help");
const help_block = document.querySelector(".overlay");
const help_close = document.querySelector(".help_close")

help.addEventListener("click" , function() {
    help_block.classList.add("active");
});

help_close.addEventListener("click" , function() {
    help_block.classList.toggle("active");
});