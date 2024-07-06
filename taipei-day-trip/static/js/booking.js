"use strict"
import { fetchResponseBearer, enableDarkMode, jump2Top, navHandler } from "./common.js";


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
        await renderBookingHTML(bookedInfo, name, email);
        await enableTappay(bookedInfo);
    } catch (error) {
        console.error("Error", error);
    }


    async function renderBookingHTML(bookedInfo, name, email) {
        await bookedInfo;
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
                        <input type="text" id="name" name="name" value="${name}" required>
                    </div>
                    <div class="form-group">
                        <label for="email">聯絡信箱 : </label>
                        <input type="email" id="email" name="email" value="${email}" required>
                    </div>
                    <div class="form-group">
                        <label for="phone">手機號碼 : </label>
                        <input type="tel" id="phone" name="phone" placeholder="0908-888-888" maxlength="12" required>
                    </div>
                    <p><b>請保持手機暢通，準時到達，導覽人員將用手機與您聯繫，務必留下正確的聯絡方式。</b></p>
                </fieldset>

                <hr class="hr">

                <fieldset class="payment-block">
                    <legend>信用卡付款資訊</legend>

                    <div class="form-group">
                        <label for="cc-number">卡片號碼 : </label>
                        <div class="tpfield" id="cc-number"></div>
                        <span id="cardtype"></span>
                    </div>
                    <div class="form-group">
                        <label for="cc-exp">過期時間 : </label>
                        <div class="tpfield" id="cc-exp"></div>
                    </div>
                    <div class="form-group">
                        <label for="cc-csc">驗證密碼 : </label>
                        <div class="tpfield" id="cc-csc"></div>
                    </div>
                </fieldset>

                <hr class="hr">

                <div class="confirm-block">
                    <div><b>總價 : 新台幣 ${bookedInfo.price} 元</b></div>
                    <button type="submit" class="form-submit">確認訂購並付款</button>
                </div>
            </form>
        `;


        document.getElementById('phone').addEventListener('input', function (e) {
            let x = e.target.value.replace(/\D/g, '').substring(0, 10);
            const regex = /^(0[2-9]\d{0,2}|09\d{2})?\d{0,8}$/;

            if (regex.test(x)) {
                if (x.length > 7) {
                  x = x.slice(0, 4) + '-' + x.slice(4, 7) + '-' + x.slice(7);
                } else if (x.length > 4) {
                  x = x.slice(0, 4) + '-' + x.slice(4);
                }
                e.target.value = x;
              } else {
                e.target.value = e.target.value.slice(0, -1); // 無効な入力の場合、最後の文字を削除
              }
        });


        // document.getElementById('phone').addEventListener('input', function (e) {
        //     let x = e.target.value.replace(/\D/g, '').substring(0, 10);
        //     const regex = /^(0[2-9]\d{2}[-]?\d{3}[-]?\d{3})$/;

        //     if (x.length > 7) {
        //         let format = x.slice(0, 4) + '-' + x.slice(4, 7) + '-' + x.slice(7);

        //         if (!regex.test(format)) {
        //             e.target.value = e.target.value.slice(0, -1); // 無効な入力の場合、最後の文字を削除
        //         } else {
        //             e.target.value = format
        //         }

        //     } else if (x.length > 4) {
        //         e.target.value = x.slice(0, 4) + '-' + x.slice(4);
        //     }
        // })


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



    //tappay

    async function enableTappay(bookedInfo) {

        fetch("/api/tappay-config")
            .then(response => response.json())
            .then(config => {
                console.log(config)
                console.log(config.APP_ID)
                console.log("==1==")
                TPDirect.setupSDK(config.APP_ID, config.APP_KEY, config.environment)
                TPDirect.card.setup({
                    fields: {
                        number: {  //elementは要素取得が目的。取得するのは本来inputのdivであることに注意
                            element: "#cc-number",
                            placeholder: "**** **** **** ****"
                        },
                        expirationDate: {
                            element: "#cc-exp",
                            placeholder: "MM / YY"
                        },
                        ccv: {
                            element: "#cc-csc",
                            placeholder: "後三碼"
                        }
                    },
                    styles: {
                        ".valid": {
                            "color": "green"
                        },
                        ".invalid": {
                            "color": "red"
                        }
                    },
                    // 顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
                    isMaskCreditCardNumber: true,
                    maskCreditCardNumberRange: {
                        beginIndex: 0,
                        endIndex: 11
                    }
                })
        
        
                TPDirect.card.onUpdate(function (update) {
        
                    if (update.canGetPrime) {
                        document.querySelector("button[type='submit']").removeAttribute("disabled");
                    } else {
                        document.querySelector("button[type='submit']").setAttribute("disabled", "true");
                    }
        
                    var newType = update.cardType === 'unknown' ? '' : update.cardType;
                    document.getElementById("cardtype").textContent = newType;
        
        
                    // number 欄位是錯誤的
                    if (update.status.number === 2) {
                        setNumberFormGroupToError("#cc-number");
                    } else if (update.status.number === 0) {
                        setNumberFormGroupToSuccess("#cc-number");
                    } else {
                        setNumberFormGroupToNormal("#cc-number");
                    }
        
                    if (update.status.expiry === 2) {
                        setNumberFormGroupToError("#cc-exp");
                    } else if (update.status.expiry === 0) {
                        setNumberFormGroupToSuccess("#cc-exp");
                    } else {
                        setNumberFormGroupToNormal("#cc-exp");
                    }
        
                    if (update.status.ccv === 2) {
                        setNumberFormGroupToError("#cc-csc");
                    } else if (update.status.ccv === 0) {
                        setNumberFormGroupToSuccess("#cc-csc");
                    } else {
                        setNumberFormGroupToNormal("#cc-csc");
                    }
                })
            })
            .catch(error => console.error("Error fetching TapPay config:", error));





        document.querySelector(".booking__form").addEventListener("submit", async function(event) {
            event.preventDefault();

            const tappayStatus = TPDirect.card.getTappayFieldsStatus();
            console.log(tappayStatus);

            // Check TPDirect.card.getTappayFieldsStatus().canGetPrime before TPDirect.card.getPrime
            if (tappayStatus.canGetPrime === false) {
                alert('can not get prime');
                return;
            }

            //TPDirect.card.getPrimeカード情報を検証し一時的なトークン(プライム)を生成しresultを返す。トークン自身はresult.card.primeにある
            TPDirect.card.getPrime(async function (result) {
                if (result.status !== 0) {   // 0 = success
                    alert('get prime error ' + result.msg);
                    return;
                }
                const url = "/api/orders"
                const formData = new FormData(event.target);
                const data = {
                    prime: result.card.prime,    //決算処理で必要なtokenでカード情報を安全に表現
                    order: {
                        price: bookedInfo.price,
                        trip: {
                            attraction: {
                                id: bookedInfo.attraction.id,
                                name: bookedInfo.attraction.name,
                                address: bookedInfo.attraction.address,
                                image: bookedInfo.attraction.image
                            },
                            date: bookedInfo.date,
                            time: bookedInfo.time
                        },
                        contact: {
                            name: formData.get("name"),
                            email: formData.get("email"),
                            phone: formData.get("phone")
                        }
                    }
                }
                const token = localStorage.getItem("jwtoken");
                fetch(url, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new HTTPError(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const orderNumber = data.data.number;
                    window.location.href = `/thankyou?number=${encodeURIComponent(orderNumber)}`;
                })
                .catch(error => {
                    if (error instanceof HttpError) {
                        console.error("HttpError", error);
                    } else {
                        console.error("Error:", error);
                    }
                });
            })
        })


        function setNumberFormGroupToError(selector) {
            document.querySelector(selector).classList.add("has-error");
            document.querySelector(selector).classList.remove("has-success");
        }

        function setNumberFormGroupToSuccess(selector) {
            document.querySelector(selector).classList.add("has-success");
            document.querySelector(selector).classList.remove("has-error");
        }

        function setNumberFormGroupToNormal(selector) {
            document.querySelector(selector).classList.remove("has-success");
            document.querySelector(selector).classList.remove("has-error");
        }

        function forceBlurIos() {
            if (!isIos()) {
                return
            }
            var input = document.createElement('input')
            input.setAttribute('type', 'text')
            // Insert to active element to ensure scroll lands somewhere relevant
            document.activeElement.prepend(input)
            input.focus()
            input.parentNode.removeChild(input)
        }

        function isIos() {
            return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        }
    }


    enableDarkMode();
    jump2Top();
});



