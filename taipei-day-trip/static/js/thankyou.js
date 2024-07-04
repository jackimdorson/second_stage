"use strict"
import { fetchResponseBearer, enableDarkMode, jump2Top, navHandler } from "./common.js";


const thankyouMainQryS = document.querySelector(".thankyou");

// ocation.searchは?p1=v1&p2=v2'を返すが、URLSearchParams.get()の方法だと?の値を引数に入力で対応する値が返る
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}


const orderNumber = getQueryParam("number");
if (orderNumber) {
    thankyouMainQryS.innerHTML =  `
        <h3>行程預定成功<br>您的訂單編號如下</h3>
        <p>${orderNumber}</p>
        <p>請記住此編號, 或到會員中信查詢歷史訂單</p>
    `;
} else {
    thankyouMainQryS.textContent = "不存在的訂單編號";
}