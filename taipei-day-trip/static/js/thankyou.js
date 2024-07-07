"use strict"
import { fetchResponseBearerJson, fetchResponseBearer, enableDarkMode, jump2Top, navHandler } from "./common.js";

document.addEventListener("DOMContentLoaded", async() => {
    navHandler.checkUserStatusByjwt();

    const thankyouMainQryS = document.querySelector(".thankyou");

    // ocation.searchは?p1=v1&p2=v2'を返すが、URLSearchParams.get()の方法だと?の値を引数に入力で対応する値が返る
    function getQuery(param) {   //数字でも返すのはstr、numが欲しかったらparseIntを使う。
        const urlQuery = new URLSearchParams(window.location.search);
        return urlQuery.get(param);
    }

    // function getPath(param) {
    //     const urlPath = window.location.pathname.split("/");  //この時点で返すのは配列
    //     return urlPath[urlPath.length - 1];   //配列の一番後ろに格納されるので-1で取得
    // }

    const orderNumber = parseInt(getQuery("number"));
    if (orderNumber > 1720000000000000) {
        thankyouMainQryS.innerHTML =  `
            <h3>行程預定成功<br>您的訂單編號如下</h3>
            <p>${orderNumber}</p>
            <p>請記住此編號, 或到會員中信查詢歷史訂單</p>
        `;
    } else {
        thankyouMainQryS.innerHTML =  `
            <h3>查詢訂單</h3>
            <form class="search-form">
                <input type="number">
                <button class="order-btn">查詢</button>
            </form>
            <br>
            <div class="search-text"></div>
        `;
    }


    document.querySelector(".search-form").addEventListener("submit", async function(event){
        event.preventDefault();
        const textQryS = document.querySelector(".search-text");
        textQryS.textContent = "";
        const orderNumberQrs = event.target.querySelector('input[type="number"]')
        const jsonData = await fetchResponseBearerJson("GET", `/api/order/${orderNumberQrs.value}`);
        if (jsonData.data){
            textQryS.innerHTML = `
                地點: ${jsonData.data.trip.attraction.name}</br>
                日期: ${jsonData.data.trip.date}</br>
                時間: ${jsonData.data.trip.time}</br>
                地址: ${jsonData.data.trip.attraction.address}</br>
                訂單: ${jsonData.data.number}
            `;
        } else {
            textQryS.textContent = "不存在的訂單編號";
        }
        orderNumberQrs.value = "";
    })




})
