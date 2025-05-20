const toast = document.querySelector(".toast");
(closeIcon = document.querySelector(".close")),
  (progress = document.querySelector(".progress"));

let timer1, timer2;

document.addEventListener('DOMContentLoaded', function() {
    const errorMessage = document.querySelector('.toast.active');
    if (errorMessage) {
        progress.classList.add("active");
        timer1 = setTimeout(() => {
          toast.classList.remove("active");
        }, 30000); //1s = 1000 milliseconds

        timer2 = setTimeout(() => {
          progress.classList.remove("active");
        }, 30300);
    }
});

closeIcon.addEventListener("click", () => {
  toast.classList.remove("active");

  setTimeout(() => {
    progress.classList.remove("active");
  }, 300);

});