import { navHandler } from "./common";
card-number
card-expiration-date
card-ccv
const ccNumber = document.getElementById("cc-number");
const ccExp = document.getElementById("cc-exp");
const ccCSC = document.getElementById("cc-csc");


fetch("/api/tappay-config")
    .then(response => response.json())
    .then(config => {
        TPDirect.setupSDK(config.APP_ID, config.APP_KEY, config.environment)
    })
    .catch(error => console.error("Error fetching TapPay config:", error));


TPDirect.card.setup({
    fields: {
        number: {  //elementはDOMみたいな役割で要素取得が目的。
            element: ccNumber,
            placeholder: "**** **** **** ****"
        },
        expirationDate: {
            element: ccExp,
            placeholder: "MM / YY"
        },
        ccv: {
            element: ccCSC,
            placeholder: "後三碼"
        }
    },  // 顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
        beginIndex: 6,
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
        setNumberFormGroupToError("#card-number");
    } else if (update.status.number === 0) {
        setNumberFormGroupToSuccess("#card-number");
    } else {
        setNumberFormGroupToNormal("#card-number");
    }

    if (update.status.expiry === 2) {
        setNumberFormGroupToError("#card-expiration-date");
    } else if (update.status.expiry === 0) {
        setNumberFormGroupToSuccess("#card-expiration-date");
    } else {
        setNumberFormGroupToNormal("#card-expiration-date");
    }

    if (update.status.ccv === 2) {
        setNumberFormGroupToError("#card-ccv");
    } else if (update.status.ccv === 0) {
        setNumberFormGroupToSuccess("#card-ccv");
    } else {
        setNumberFormGroupToNormal("#card-ccv");
    }
})

document.querySelector("form").addEventListener("submit", function(event){
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
        if (result.status !== 0) {
            alert('get prime error ' + result.msg);
            return;
        }
        const url = "/api/orders"
        const data = {
            prime: result.card.prime,    //決算処理で必要なtokenでカード情報を安全に表現
            order: {
                price: "",
                trip: {
                    attraction: {
                        id: "",
                        name: "",
                        address: "",
                        image: ""
                    },
                    date: "",
                    time: ""
                },
                contact: {
                    name: "",
                    email: "",
                    phone: ""
                }
            }
        }

        fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data)
            })
        .then(response => {
            if (!response.ok) {
                throw new HTTPError(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => console.log("Success:", data))
        .catch(error => {
            if (error instanceof HttpError) {
                console.error("HttpError", error);
            } else {
                console.error("Error:", error);
            }
        });
    })
})
        // try{
        //     const response = await fetch(url, {
        //         method: "POST",
        //         headers: {
        //             "Content-Type": "application/json",
        //             "x-api-key": "partner_6ID1DoDlaPrfHw6HBZsULfTYtDmWs0q0ZZGKMBpp4YICWBxgK97eK3RM"
        //         },
        //         body: JSON.stringify(data)
        //     })

        //     if (!response.ok) {
        //         throw new Error(`HTTP error! status: ${response.status}`);
        //     }
        //     const responseData = await response.json();
        //     console.log("Success:", responseData);

        // } catch (error) {
        //     console.error("Error", error);
        // }


//         var command = `
//         Use following command to send to server \n\n
//         curl -X POST https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime \\
//         -H 'content-type: application/json' \\
//         -H 'x-api-key: partner_6ID1DoDlaPrfHw6HBZsULfTYtDmWs0q0ZZGKMBpp4YICWBxgK97eK3RM' \\
//         -d '{
//             "partner_key": "partner_6ID1DoDlaPrfHw6HBZsULfTYtDmWs0q0ZZGKMBpp4YICWBxgK97eK3RM",
//             "prime": "${result.card.prime}",
//             "amount": "1",
//             "merchant_id": "GlobalTesting_CTBC",
//             "details": "Some item",
//             "cardholder": {
//                 "phone_number": "+886923456789",
//                 "name": "王小明",
//                 "email": "LittleMing@Wang.com",
//                 "zip_code": "100",
//                 "address": "台北市天龍區芝麻街1號1樓",
//                 "national_id": "A123456789"
//             }
//         }'`.replace(/                /g, '')
//         document.querySelector('#curl').innerHTML = command
//     })
// })

function setNumberFormGroupToError(selector) {
    document.querySelector(selector).addClass("has-error");
    document.querySelector(selector).removeClass("has-success");
}

function setNumberFormGroupToSuccess(selector) {
    document.querySelector(selector).addClass("has-success");
    document.querySelector(selector).removeClass("has-error");
}

function setNumberFormGroupToNormal(selector) {
    document.querySelector(selector).removeClass("has-success");
    document.querySelector(selector).removeClass("has-error");
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
