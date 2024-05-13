const leftbtn = document.querySelector('.btn-left');
const rightbtn = document.querySelector('.btn-right');
const carousel = document.querySelector('.carousel');
const mainDiv = document.querySelector('.main-div');
let timeRunning = 1500;
let runTimeOut;

leftbtn.addEventListener('click', () => {
    showSlide('prev');
});

rightbtn.addEventListener('click', () => {
    showSlide('next');
});

function showSlide(type) {
    let slides = document.querySelectorAll('.carousel .main-div .carousel-item');
    if (type === 'next') {
        mainDiv.appendChild(slides[0]);
        carousel.classList.add('next');
    } else {
        mainDiv.prepend(slides[slides.length - 1]);
        carousel.classList.add('prev');
    }
    
    clearTimeout(runTimeOut);
    runTimeOut = setTimeout(() => {
        carousel.classList.remove('next');
        carousel.classList.remove('prev');
    }, timeRunning);
}