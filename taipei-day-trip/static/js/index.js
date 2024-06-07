"use strict"

// document.addEventListener("DOMContentLoaded", function() {
//     const link = document.createElement("link");
//     link.href = "https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap";
//     link.rel = "stylesheet";
//     document.head.appendChild(link);
//   });


const tabsQryS = document.querySelector(".tabs")
const clickAttrQryS = document.querySelector(".search-box__icon");
const inputAttrQryS = document.querySelector(".search-box__input");


async function fetchAttractions(pageArg, keywordArg = null){
    let url = `/api/attractions?page=${encodeURIComponent(pageArg)}`;
    if (keywordArg) {
        url += `&keyword=${encodeURIComponent(keywordArg)}`;
    }
    const response = await fetch(url);
    const jsonData = await response.json();
    return jsonData;
}


let page = 0;
let keyword = null;

async function loadMoreItems(pageArg, keywordArg = null) {   //非同期関数のreturnはawaitで処理しても常にPromiseを返す
    try {
        const jsonData = await fetchAttractions(pageArg, keywordArg);       // fetch().dataとする事はできない。
        if (!jsonData.data) {
            tabsQryS.textContent = jsonData.message;
            throw Error;
        }
        const attractionsList = jsonData.data;
        const totalItems = attractionsList.length;
        const fragment = document.createDocumentFragment();  //DocumentFragmentを使用してDOM操作を効率化。直接appendChildを使用すると12回の再描画が発生しますが、DocumentFragmentを使用すると1回の再描画で済む。

        for (let i = 0; i < totalItems; i++) {
            const attraction = attractionsList[i];
            const parentElmDiv = createParentsElmDiv(attraction);
            fragment.appendChild(parentElmDiv);
        }
        tabsQryS.appendChild(fragment);   //appendChildは再描画しないといけない為、fragment経由で一度にDOMに追加
        let abc = jsonData.nextPage;
        return abc;
    } catch (error) {
        console.error('Error loading more items:', error);
        return null;
    }
}


function createElmAndClass(elm, className) {
    const element = document.createElement(elm);
    element.classList.add(className);      // classList.addの戻り値はundefinedの為, createElementと一緒に書けない。
    return element;
}


function createParentsElmDiv(attraction) {
    const parentElmDiv = createElmAndClass("article", "tabs__item");

    const childElmImg = createElmAndClass("img", "tabs__img");
    childElmImg.src = attraction.images[0];
    childElmImg.alt = attraction.name;
    childElmImg.loading = "lazy";
    parentElmDiv.appendChild(childElmImg);   //appendChildの頻度の多くないところでは、影響が少ない為fragment経由でなくても良い

    const childElmDivName = createElmAndClass("div", "tabs__name");
    childElmDivName.textContent = attraction.name;
    parentElmDiv.appendChild(childElmDivName);

    const childElmDivInfo = createElmAndClass("div", "tabs__info");
    const childElmDivMrt = createElmAndClass("div", "tabs__mrt");
    childElmDivMrt.textContent = attraction.mrt;
    const childElmDivCategory = createElmAndClass("div", "tabs__category");
    childElmDivCategory.textContent = attraction.category;
    childElmDivInfo.appendChild(childElmDivCategory);
    childElmDivInfo.appendChild(childElmDivMrt);

    parentElmDiv.appendChild(childElmDivInfo);
    return parentElmDiv;
}



document.addEventListener("DOMContentLoaded", async () => {    //loadMoreItemsは非同期関数で、関数は常にPromiseを返す為、内部でawaitしても、再度awaitする必要あり。
    const footer = document.querySelector(".footer");    // 監視する対象

    const options = {        // IntersectionObserverの設定
        root: null,          // null=viewport(ブラウザの表示領域)をルートとして使用
        rootMargin: "0px",
        threshold: 0.7       // 1.0=ターゲットが 100% 表示された時にコールバックが呼び出される
    }

    const callback = async (entries, observer) => {
        for (const entry of entries) {
            if (entry.isIntersecting) {    //要素がviewportに入っている
                if (page !== null) {
                    page = await loadMoreItems(page, keyword);
                }
            }
        }
    }

    const observer = new IntersectionObserver(callback, options);
    observer.observe(footer);
        page = await loadMoreItems(page, keyword);
});


clickAttrQryS.addEventListener("click", async function() {
    page = 0;
    keyword = inputAttrQryS.value;
    tabsQryS.textContent = "";
    inputAttrQryS.value = "";
    page = await loadMoreItems(page, keyword);
})



document.addEventListener("DOMContentLoaded", async () => {
    const carouselTrack = document.querySelector('.carousel__track');
    const leftButton = document.querySelector('.carousel__button--left');
    const rightButton = document.querySelector('.carousel__button--right');

    const response = await fetch("/api/mrts");
    const jsonData = await response.json();
    const stationsList = jsonData.data;
    const fragment = document.createDocumentFragment();

    for (const stationList of stationsList) {
        const div = document.createElement("div");
        div.classList.add("carousel__item");
        div.textContent = stationList;
        fragment.appendChild(div);
    }
    carouselTrack.appendChild(fragment);


    const getScrollAmount = () => {
        if (window.innerWidth >= 1200) {
            return 10;
        } else if (window.innerWidth <= 500) {
            return 2;
        } else {
            return 4;
        }
    }


    let currentIndex = 0;    // 現在表示されているカルーセルアイテムのインデックスを保持
    const updateCarousel = () => {   //カルーセルの位置を更新するための関数
        const width = carouselTrack.children[0].getBoundingClientRect().width;  //カルーセルアイテムの幅を取得(各アイテムは同じ幅で設計されることがほとんど).getBoundingClientRect()は要素のサイズと位置を含むDOMRectオブジェクトを返す
        carouselTrack.style.transform = `translateX(-${currentIndex * width}px)`;  //カルーセルの位置の更新
    }
    leftButton.addEventListener("click", () => {
        const scrollAmount = getScrollAmount();
        if (currentIndex > 0) {
            currentIndex = Math.max(0, currentIndex - scrollAmount);
            updateCarousel();
        }
    })
    rightButton.addEventListener("click", () => {
        const scrollAmount = getScrollAmount();
        if (currentIndex < stationsList.length - scrollAmount - 3) {   //3は最後の微調整
            currentIndex = Math.min(stationsList.length - scrollAmount, currentIndex + scrollAmount);
            updateCarousel();
        }
    })
    carouselTrack.addEventListener("click", async(event) => {
        if (event.target.classList.contains("carousel__item")) {
            keyword = event.target.textContent;
            inputAttrQryS.value = keyword;
            page = 0;
            tabsQryS.textContent = "";
            page = await loadMoreItems(page, keyword);
        }
    })
})

// addEventListenerには2つの方法がある。// 要素が1〜3つしかない場合: => 子要素に対して使う。
//要素が複数あり、for文などを必要とする場合: => 親要素に対して使い、eventで小要素を操作。
// 以下の方法では、各イベントリスナーが個別に処理されるため、イベントが発生するたびに30個のリスナーがチェックされる。
// const clickMrtsQrySA = document.querySelectorAll(".carousel__item");
// for (const clickMrtQryS of clickMrtsQrySA){
