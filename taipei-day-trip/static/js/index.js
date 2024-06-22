"use strict"
import { fetchResponseJson, preloadImage, createElmAndClass, debounce, enableDarkMode, jump2Top, checkUserStatusByjwt } from "./common.js";

const cardsQryS = document.querySelector(".cards");
const inputAttrQryS = document.querySelector(".search-box__input");
const clickAttrQryS = document.querySelector(".search-box__icon");
const carouselTrack = document.querySelector('.carousel__track');


function makeUrl(pageArg, keywordArg) {
    let url = `/api/attractions?page=${encodeURIComponent(pageArg)}`;
    if (keywordArg) {
        url += `&keyword=${encodeURIComponent(keywordArg)}`;
    }
    return url;
}

function createParentsElmDiv(attraction) {
    const parentElmDiv = createElmAndClass("a", "cards__link");
    parentElmDiv.href = `/attraction/${attraction.id}`;

    const childElmImg = createElmAndClass("img", "cards__img");
    childElmImg.src = attraction.images[0];
    childElmImg.alt = attraction.name;
    childElmImg.loading = "lazy";
    parentElmDiv.appendChild(childElmImg);   //appendChildの頻度の多くないところでは、影響が少ない為fragment経由でなくても良い

    const childElmDivName = createElmAndClass("div", "cards__name");
    childElmDivName.textContent = attraction.name;
    parentElmDiv.appendChild(childElmDivName);

    const childElmDivInfo = createElmAndClass("div", "cards__info");
    const childElmDivMrt = createElmAndClass("div", "cards__mrt");
    childElmDivMrt.textContent = attraction.mrt;
    const childElmDivCategory = createElmAndClass("div", "cards__category");
    childElmDivCategory.textContent = attraction.category;
    childElmDivInfo.appendChild(childElmDivCategory);
    childElmDivInfo.appendChild(childElmDivMrt);

    parentElmDiv.appendChild(childElmDivInfo);
    return parentElmDiv;
}

async function loadNextPage(pageArg, keywordArg) {   //非同期関数のreturnはawaitで処理しても常にPromiseを返す
    const url = makeUrl(pageArg, keywordArg);
    const jsonData = await fetchResponseJson(url);
    if (!jsonData.data) {
        cardsQryS.textContent = jsonData.message;
        return null;
    }
    const fragment = document.createDocumentFragment();  //DocumentFragmentを使用してDOM操作を効率化。直接appendChildを使用すると12回の再描画が発生しますが、DocumentFragmentを使用すると1回の再描画で済む。
    for (const attraction of jsonData.data) {
        preloadImage(attraction.images[0]);
        const parentElmDiv = createParentsElmDiv(attraction);
        fragment.appendChild(parentElmDiv);
    }
    cardsQryS.appendChild(fragment);   //appendChildは再描画しないといけない為、fragment経由で一度にDOMに追加
    return jsonData.nextPage;
}


document.addEventListener("DOMContentLoaded", async () => {    //loadNextPageは非同期関数で、関数は常にPromiseを返す為、内部でawaitしても、再度awaitする必要あり。
    checkUserStatusByjwt();   //顯示畫面就馬上檢查UserStatus
    let page = 0;
    let keyword = null;
    page = await loadNextPage(page, keyword);   //0ページ目の読み込み(homepage入った時の)

    //透過往下滑方式抓data
    const footer = document.querySelector(".footer");    // 監視する対象
    const options = {        // IntersectionObserverの設定（どのくらい重なると『交差した』ことにするのか）
        root: null,          // null=viewport(ブラウザの表示領域)をルートとして使用
        rootMargin: "0px",
        threshold: 0.5       // 1.0=ターゲットが 100% 表示された時にコールバックが呼び出される
    }
    const callback = debounce(async (entries, observer) => {
        for (const entry of entries) {     //intersectingは交差しているかの真偽値を返す
            if (entry.isIntersecting && page !== null) {    //要素がviewportに入っている
                page = await loadNextPage(page, keyword);
            }
        }
    }, 400)  //タイマーがカウントダウンの終わりに達すると、デバウンス関数が実行
    const observer = new IntersectionObserver(callback, options);  //callbackは交差のon/off時に発生
    observer.observe(footer);


    //透過SearchBox方式抓data
    async function handleClick() {
        page = 0;
        keyword = inputAttrQryS.value;
        cardsQryS.textContent = "";
        inputAttrQryS.value = "";
        page = await loadNextPage(page, keyword);
    }

    function handleKeydown(event) {
        if (event.key === "Enter"){
            clickAttrQryS.click();
        }
    }
    clickAttrQryS.addEventListener("click", debounce(handleClick, 400));
    inputAttrQryS.addEventListener("keydown", debounce(handleKeydown, 400));

    //透過List Bar方式抓data
    const leftButton = document.querySelector('.carousel__button--left');
    const rightButton = document.querySelector('.carousel__button--right');
    const jsonData = await fetchResponseJson("/api/mrts");
    const fragment = document.createDocumentFragment();

    for (const stationList of jsonData.data) {
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

    const updateCarousel = (direction) => {   //カルーセルの位置を更新するための関数
        const width = carouselTrack.children[0].getBoundingClientRect().width;  //カルーセルアイテムの幅を取得(各アイテムは同じ幅で設計されることがほとんど).getBoundingClientRect()は要素のサイズと位置を含むDOMRectオブジェクトを返す
        const scrollAmount = getScrollAmount() * width;
        carouselTrack.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' });  //カルーセルの位置の更新-は左に移動の意味
    }

    leftButton.addEventListener("click", () => {
        updateCarousel(-1);
    })

    rightButton.addEventListener("click", () => {
        updateCarousel(1);
    })

    async function showOnSearchBox(event) {
        if (event.target.classList.contains("carousel__item")) {
            keyword = event.target.textContent;
            inputAttrQryS.value = keyword;
            page = 0;
            cardsQryS.textContent = "";
            page = await loadNextPage(page, keyword);
        }
    }
    carouselTrack.addEventListener("click", debounce(showOnSearchBox, 400));
    enableDarkMode();
    jump2Top();
})


// addEventListenerには2つの方法がある。// 要素が1〜3つしかない場合: => 子要素に対して使う。
//要素が複数あり、for文などを必要とする場合: => 親要素に対して使い、eventで小要素を操作。
// 以下の方法では、各イベントリスナーが個別に処理されるため、イベントが発生するたびに30個のリスナーがチェックされる。
// const clickMrtsQrySA = document.querySelectorAll(".carousel__item");
// for (const clickMrtQryS of clickMrtsQrySA){
