"use strict"

const tabsQryS = document.querySelector(".tabs")
const clickAttrQryS = document.querySelector(".search-box__icon");
const inputAttrQryS = document.querySelector(".search-box__input");


async function fetchAttractions(pageArg, keywordArg = null){
    console.log(pageArg);
    console.log("--2--")
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
    const parentElmDiv = createElmAndClass("div", "tabs__items");

    const childElmImg = createElmAndClass("img", "tabs__img");
    childElmImg.src = attraction.images[0];
    childElmImg.alt = attraction.name;
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
    const stations = data.data;

})