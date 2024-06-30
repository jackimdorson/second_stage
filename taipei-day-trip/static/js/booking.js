"use strict"
import { fetchResponseJson, fetchResponseBearer, preloadImage, createElmAndClass, debounce, enableDarkMode, jump2Top, navHandler } from "./common.js";


document.addEventListener("DOMContentLoaded", async() => {
    const bookingQry = document.querySelector(".booking");
    const jsonData = await navHandler.checkUserStatusByjwt();
    if (!jsonData.data) {
        window.location.href = "/";
    }
    const spanUsernameQryS = document.querySelector(".book__username");
    const {id, name, email} = jsonData.data;
    spanUsernameQryS.textContent = name;
    try {
        const bookedData = await fetchResponseBearer("GET", "/api/booking");
        if (!bookedData.data) {
            return bookingQry.textContent = "目前沒有任何待預定的行程";
        }
        const bookedInfo = await bookedData.data;
        renderBookingHTML(bookedInfo, name, email);
    } catch (error) {
        console.error("Error", error);
    }



async function renderBookingHTML(bookedInfo, name, email) {
    await bookedInfo;
    console.log(bookedInfo);
    bookedInfo.time = bookedInfo.time === "morning" ? "早上9點到下午4點" : "下午2點到下午9點";
    bookingQry.innerHTML = `
        <section class="attraction-block">
            <img class="attraction-block__img" src="${bookedInfo.attraction.image}">
            <div class="attraction-block__info">
                <p><b>台北一日遊 : ${bookedInfo.attraction.name}</b></p>
                <p><b>日期 : </b>${bookedInfo.date}</p>
                <p><b>時間 : </b>${bookedInfo.time}</p>
                <p><b>費用 : </b>新台幣 ${bookedInfo.price} 元</p>
                <p><b>地點 : </b>${bookedInfo.attraction.address}</p>
                <button class="delete-btn">
                    <img src="/static/images/icons/delete30x30.webp">
                </button>
            </div>
        </section>
        <hr class="hr">
        <form class="booking__form">
            <fieldset class="contact-block">
                <legend>您的聯絡資訊</legend>
                <div class="form-group">
                    <label for="name">聯絡姓名 : </label>
                    <input type="text" id="name" value="${name}" required>
                </div>
                <div class="form-group">
                    <label for="email">聯絡信箱 : </label>
                    <input type="email" id="email" value="${email}" required>
                </div>
                <div class="form-group">
                    <label for="phone">手機號碼 : </label>
                    <input type="tel" id="phone" required placeholder="0908-888-888">
                </div>
                <p><b>請保持手機暢通，準時到達，導覽人員將用手機與您聯繫，務必留下正確的聯絡方式。</b></p>
            </fieldset>

            <hr class="hr">

            <fieldset class="payment-block">
                <legend>信用卡付款資訊</legend>
                <div class="form-group">
                    <label for="cc-number">卡片號碼 : </label>
                    <input id="cc-number" autocomplete="cc-number" type="text" inputmode="numeric" pattern="[0-9\s]{13,19}" maxlength="19" placeholder="**** **** **** ****" required>
                </div>
                <div class="form-group">
                    <label for="cc-exp">過期時間 : </label>
                    <input id="cc-exp" autocomplete="cc-exp" type="text" placeholder="MM / YY" pattern="(0[1-9]|1[0-2])\/[0-9]{2}" maxlength="5" required>
                </div>
                <div class="form-group">
                    <label for="cc-csc">驗證密碼 : </label>
                    <input id="cc-csc" autocomplete="cc-csc" type="text" inputmode="numeric" pattern="[0-9]{3,4}" maxlength="4" placeholder="CVV" required>
                </div>
            </fieldset>

            <hr class="hr">

            <div class="confirm-block">
                <div><b>總價 : 新台幣 ${bookedInfo.price} 元</b></div>
                <button type="submit" class="form-submit">確認訂購並付款</button>
            </div>
        </form>
    `;

    const deleteBtn = document.querySelector(".delete-btn");
    const handledeleteClick = async () => {
        const jsonData = await navHandler.checkUserStatusByjwt();
        if (!jsonData.data) {
            window.location.href = "/";
        }
        try {
            await fetchResponseBearer("DELETE", "/api/booking");
            await new Promise(resolve => setTimeout(async () => {
                    window.location.reload();   //整個畫面都reflesh會下降UX
                    resolve();
            }, 10));
        } catch (error) {
            console.error("Error", error);
        }
    }
    deleteBtn.addEventListener("click", handledeleteClick)

}
});
    // document.querySelector(".booking__form").addEventListener("submit", (event) => {
    //     event.preventDefault();
    // })
