"use strict"
import { fetchResponseJson, fetchResponseBearerJson, preloadImage, createElmAndClass, enableDarkMode, jump2Top, navHandler } from "./common.js";

document.addEventListener("DOMContentLoaded", async () => {    //loadNextPageは非同期関数で、関数は常にPromiseを返す為、内部でawaitしても、再度awaitする必要あり。
    navHandler.checkUserStatusByjwt();

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
        const jsonData = await fetchResponseJson("GET", `/api/attraction/${attractionId}`);
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

    document.querySelector(".schedule__time").addEventListener("change", () => {
        priceSpan.textContent = `新台幣 ${document.querySelector('input[type="radio"]:checked').value} 元`
    })


    async function responseJwtUserInfo(event){
        event.preventDefault();
        const jsonData = await navHandler.checkUserStatusByjwt();
        if (!jsonData.data) {
            navHandler.showSigninForm();
            return null;
        }
        const attractionId = window.location.pathname.split("/").pop();  //...pathname＝http://example.com/acb/10の場合, /abc/10を取得しpopで最後の要素を取得
        const {id, name, email} = jsonData.data;
        const price = document.querySelector('input[type="radio"]:checked').value;
        const priceMap = { 2000: "morning", 2500: "afternoon" }

        const formData = {
            attractionId: parseInt(attractionId),   //文字列を整数に変換
            date: document.getElementById("date").value,
            time: priceMap[price],
            price: parseInt(price),
            userId: parseInt(id)
        }

        const response = await fetchResponseBearerJson("POST", "/api/booking", formData);
        if (response.ok) {
            window.location.href = "/booking";
        }
    }
    document.querySelector(".attraction__form").addEventListener("submit", responseJwtUserInfo);

    enableDarkMode();
    jump2Top();
})