"use strict"

const tabsQryS = document.querySelector(".tabs");
const inputAttrQryS = document.querySelector(".search-box__input");
const clickAttrQryS = document.querySelector(".search-box__icon");
const carouselTrack = document.querySelector('.carousel__track');
const leftButton = document.querySelector('.carousel__button--left');
const rightButton = document.querySelector('.carousel__button--right');

let currentController = null;  // AbortControllerで必要: 初期状態ではコントローラが存在しないことを示す //各リクエストに対して個別に宣言する必要あり。

async function fetchWithAbort(url, controller) {   //controllerはcurrentControllerを受けるための単なる引数
    const response = await fetch(url, { signal: controller.signal }); //fetchリクエストにAbortSignalを渡す事でAbortControllerを使用してリクエストを中断が可能に
    if (!response.ok) {
        throw new Error(`HTTP Error status:${response.status}`);
    }
    return response.json();
}

async function fetchAttractions(pageArg, keywordArg, controller){
    let url = `/api/attractions?page=${encodeURIComponent(pageArg)}`;
    if (keywordArg) {
        url += `&keyword=${encodeURIComponent(keywordArg)}`;
    }
    return fetchWithAbort(url, controller);
}

// async function fetchMrtStations(controller) {
//     const url = "/api/mrts";
//     return fetchWithAbort(url, controller);
// }

let page = 0;
let keyword = null;
async function loadMoreItems(pageArg, keywordArg) {   //非同期関数のreturnはawaitで処理しても常にPromiseを返す
    if (currentController) {    //trueでないと実行されない事に注意, nullでは挙動しない
        currentController.abort();   //新しいリクエストが発生するたび、前のリクエストをキャンセルするためにcurrentController.abort()を呼び出す
    }
    currentController = new AbortController();   //新しいAbortControllerを作成

    try {
        const jsonData = await fetchAttractions(pageArg, keywordArg, currentController);       // fetch().dataとする事はできない。
        if (!jsonData.data) {
            tabsQryS.textContent = jsonData.message;
            throw new Error("無資料");
        }
        const attractionsList = jsonData.data;
        const fragment = document.createDocumentFragment();  //DocumentFragmentを使用してDOM操作を効率化。直接appendChildを使用すると12回の再描画が発生しますが、DocumentFragmentを使用すると1回の再描画で済む。

        for (const attractionList of attractionsList) {
            const parentElmDiv = createParentsElmDiv(attractionList);
            fragment.appendChild(parentElmDiv);
        }
        tabsQryS.appendChild(fragment);   //appendChildは再描画しないといけない為、fragment経由で一度にDOMに追加
        return jsonData.nextPage;
    } catch (error) {
        if (error.name === "AbortError") {
            console.log("Fetch aborted");
        } else {
            console.error("Fetch error:", error);
        }
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
    page = await loadMoreItems(page, keyword);   //0ページ目の読み込み(homepage入った時の)

    //透過往下滑方式抓data
    const footer = document.querySelector(".footer");    // 監視する対象
    const options = {        // IntersectionObserverの設定
        root: null,          // null=viewport(ブラウザの表示領域)をルートとして使用
        rootMargin: "0px",
        threshold: 0.5       // 1.0=ターゲットが 100% 表示された時にコールバックが呼び出される
    }
    const callback = async (entries, observer) => {
        for (const entry of entries) {
            if (entry.isIntersecting && page !== null) {    //要素がviewportに入っている
                page = await loadMoreItems(page, keyword);
            }
        }
    }
    const observer = new IntersectionObserver(callback, options);
    observer.observe(footer);

    //透過SearchBox方式抓data
    clickAttrQryS.addEventListener("click", async function() {
        page = 0;
        keyword = inputAttrQryS.value;
        tabsQryS.textContent = "";
        inputAttrQryS.value = "";
        page = await loadMoreItems(page, keyword);
    })
    inputAttrQryS.addEventListener("keydown", function(event) {
        if (event.key === "Enter"){
            clickAttrQryS.click();
        }
    })


    //透過List Bar方式抓data
    const response = await fetch("/api/mrts");
    const jsonData = await response.json();
    const stationsList = jsonData.data;
    const fragment = document.createDocumentFragment();

    for (const stationList of stationsList) {
        const elmLi = createElmAndClass("li", "carousel__item");
        elmLi.textContent = stationList;
        fragment.appendChild(elmLi);
    }
    carouselTrack.appendChild(fragment);


    const getScrollAmount = () => {
        if (window.innerWidth >= 1200) {
            return 12;
        } else if (window.innerWidth >= 700) {
            return 8;
        } else if (window.innerWidth >= 500) {
            return 4;
        } else {
            return 2;
        }
    }

    let currentIndex = 0;    // 現在表示されているカルーセルアイテムのインデックスを保持
    const updateCarousel = () => {   //カルーセルの位置を更新するための関数
        const width = carouselTrack.children[0].getBoundingClientRect().width;  //カルーセルアイテムの幅を取得(各アイテムは同じ幅で設計されることがほとんど).getBoundingClientRect()は要素のサイズと位置を含むDOMRectオブジェクトを返す
        carouselTrack.style.transform = `translateX(-${currentIndex * width}px)`;  //カルーセルの位置の更新-は左に移動の意味
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
        if (currentIndex < stationsList.length - scrollAmount) {
            currentIndex = Math.min(stationsList.length - scrollAmount - 2, currentIndex + scrollAmount);   //2は最後の微調整
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
