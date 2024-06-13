"use strict"
import { fetchResponseJson, preloadImage, createElmAndClass } from "./common.js";

const attractionQryS = document.querySelector(".attraction");
const titleQryS = document.querySelector(".attraction__title");
const catQryS = document.querySelector(".attraction__cat");
const mrtQryS = document.querySelector(".attraction__mrt");
const descQryS = document.querySelector(".info__description");
const addressQryS = document.querySelector(".info__address");
const transportQryS = document.querySelector(".info__transport");

async function fetchAttractionId(){
    const path = window.location.pathname;  //   /attraction/1を取得
    const attractionId = path.split('/').pop();     //  1を取得
    if (!attractionId) {
        return null;
    }
    const jsonData = await fetchResponseJson(`/api/attraction/${attractionId}`);
    if (!jsonData.data) {
        attractionQryS.textContent = jsonData.message;
        return null;
    }
    for (const imageUrl of jsonData.data.images){
        const li = document.createElement("li");
        li.classList.add("carousel__slide");
        const img = document.createElement("img");
        img.classList.add("carousel__img");
        img.src = imageUrl;
        img.alt = jsonData.data.name;
        li.appendChild(img);
        carouselTrackQryS.appendChild(li);
    }
    for (let i = 0; i < 3; i++) {
        preloadImage(jsonData.data.images[i]);
    }
    titleQryS.textContent = jsonData.data.name;
    catQryS.textContent = jsonData.data.category;
    mrtQryS.textContent = ` at ${jsonData.data.mrt}`;
    descQryS.textContent = jsonData.data.description;
    addressQryS.textContent = jsonData.data.address;
    transportQryS.textContent = jsonData.data.transport;

    initializeCarousel();
}
fetchAttractionId();

// カルーセルの動作を制御
const carouselTrackQryS = document.querySelector(".carousel__track");
const prevButton = document.querySelector('.carousel__button--left');
const nextButton = document.querySelector('.carousel__button--right');
const navQryS = document.querySelector('.carousel__nav');
let slides = [];
let indicators = [];
let currentIndex = 0;

const initializeCarousel = () => {
    slides = Array.from(carouselTrackQryS.children);
    createIndicators();
    attachEventListeners();
    updateCarousel();
}

const createIndicators = () => {
    for (let index = 0; index < slides.length; index++) {  //indicator(...)の作成
        const indicator = createElmAndClass("div", "carousel__indicator");
        if(index === 0){
            indicator.classList.add("carousel__indicator--active");
        }
        navQryS.appendChild(indicator);
        indicators.push(indicator);

        indicator.addEventListener("click", () => {
            currentIndex = index;
            updateCarousel();
        })
    }
}

const updateCarousel = () => {     //transformはGPUで処理する為、scrollByより良い
    const slideWidth = slides[0].getBoundingClientRect().width;
    carouselTrackQryS.style.transform = `translateX(-${slideWidth * currentIndex}px)`;
    updateIndicators();
};

const updateIndicators = () => {
    for (let index = 0; index < indicators.length; index++) {
        const indicator = indicators[index];
        indicator.classList.toggle("carousel__indicator--active", index === currentIndex);
    }
}

const attachEventListeners = () => {
    prevButton.addEventListener("click", () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    })

    nextButton.addEventListener("click", () => {
        if (currentIndex < slides.length - 1) {
            currentIndex++;
            updateCarousel();
        }
    })
    const resizeObserver = new ResizeObserver(() => {
        carouselTrackQryS.classList.add("carousel__track--disable");
        updateCarousel();
        // 次のリフレッシュフレームでtransitionを元に戻す
        requestAnimationFrame(() => {
            carouselTrackQryS.classList.remove("carousel__track--disable");
        });
    });
    resizeObserver.observe(carouselTrackQryS);
};


const priceSpan = document.querySelector(".schedule__price--text");
const priceMap = {
    morning: "新台幣 2000 元",
    evening: "新台幣 2500 元"
}

document.querySelector(".schedule__time").addEventListener("change", function(event){
    if (event.target.name === "selectday") {
        priceSpan.textContent = priceMap[event.target.value];
    }
})