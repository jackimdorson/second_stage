/* moduleを使うには、『呼び出したいファイル』の<script>タグにtype="module"属性を追加する必要あり */

export async function fetchResponseJson(method, url, body = null) {
    const format = {
        method: method,
        headers: {"Content-Type": "application/json"}
    }
    if (method !== "GET" && body) {
        format.body = JSON.stringify(body);
    }
    try {
        const response = await fetch(url, format);  // fetchの前にresponse.okを記述すると200番以外はfalse(400.500)
        const jsonData = await response.json();
        if(!response.ok) {
            throw new Error (jsonData.message || `內部連線出錯 HTTP Error status: ${response.status}`);
        }  //backEndでErrorMsgとstatusCodeを一貫させることでこのような記述が可能になる
        return jsonData;
    } catch (error) {  // error = エラーmsg, error場所が含まれる
        console.error("Fetch Error", error);  //console.error(赤)は、エラーmsgをコンソールに出力するための関数
        return {"error": true, "message": error.message};
    }  //error.message は throw new Errorで投げられたmsgを取得可能な組み込みメソッド
}


export async function fetchResponseBearer(url) {
    const token = localStorage.getItem("jwtoken");
    try {
        const response = await fetch(url, {
            method: "GET",   // APIリクエストのヘッダーにJWTを含める
            headers: {"Authorization": `Bearer ${token}`}  //　JWTをheaderに含めてリクエストを送信
        });
        if (!response.ok) {   // 200番以外の時にError, but200番で空の場合はNot Error
            throw new Error(`內部連線出錯 HTTP Error status: ${response.status}`);
        }
        return response.json();
    } catch(error) {
        console.error("Fetch Error", error);
    }
}


export const preloadImage = (imgSrc) => {
    const link = document.createElement("link");
    link.rel = "preload";
    link.href = imgSrc;
    link.as = "image";
    document.head.appendChild(link);
}


export function createElmAndClass(elm, className) {
    const element = document.createElement(elm);
    element.classList.add(className);   // classList.addの戻り値はundefinedの為, createElementと一緒に書けない。
    return element;
}


export function debounce(func, wait) {   //関数とwait時間を受け取り、発生した複数のイベントを1回のイベントにまとめる
    let timeout;   //timerを格納する変数
    return function(...args){    //任意の引数を受け取るの意味。
        clearTimeout(timeout);   //タイマーが期限切れになる前に新しいイベントが発生すると、タイマーはリセット
        timeout = setTimeout(() => func.apply(this, args), wait);  //新しいタイマーを設定し、ウェイト時間後に関数を実行
    }
}


export function enableDarkMode() {
    const btnDark = document.querySelector(".darkmode-btn");
    const imgElm = document.createElement("img");
    imgElm.alt = "theme-mode";
    btnDark.appendChild(imgElm);

    const getImage = (imgElm, mode) => {
        imgElm.src = mode === "dark" ? "/static/images/icons/mode-dark32x32.webp" : "/static/images/icons/mode-light32x32.webp";
    }

    const setTheme = (mode) => {
        document.documentElement.setAttribute("data-theme", mode);  //data-theme = themeを扱うhtml属性
        getImage(imgElm, mode);
        localStorage.setItem("theme", mode);
    }

    const initialMode = localStorage.getItem("theme") || document.documentElement.getAttribute("data-theme");
    setTheme(initialMode);

    btnDark.addEventListener("click", () => {
        const modeNow = document.documentElement.getAttribute("data-theme");
        const updateMode = modeNow === "dark" ? "light" : "dark";     //trueならlightに、falseならdarkに
        setTheme(updateMode);
    })
}


export function jump2Top() {
    const toTopBtn = document.querySelector(".jump2top-btn");
    const imgElm = document.createElement("img");
    imgElm.alt = "jump-btn";
    imgElm.src = "/static/images/icons/to-top96x96.webp";
    toTopBtn.appendChild(imgElm);

    let countingDown;
    const COUNT_DOWN_FLASH = 400;
    const COUNT_DOWN_HIDE = 2000;

    function displayBlock() {
        toTopBtn.style.display = "block";
    }

    function displayNone(){
        toTopBtn.style.display = "none";
    }

    const handleScroll = debounce(() => {
        clearTimeout(countingDown); //  setTimeout(hideButtonがカウントしてる際にscrollが起きればclear
        if (toTopBtn.style.display === "none") {
            setTimeout(displayBlock, COUNT_DOWN_FLASH);
        }
        countingDown = setTimeout(displayNone, COUNT_DOWN_HIDE);
    }, COUNT_DOWN_FLASH)

    window.addEventListener("scroll", handleScroll);
    toTopBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    })
}


class SignPopup {
    constructor(navSignpopQryS, navHandler) {
        this.navSignpopQryS = navSignpopQryS;
        this.navHandler = navHandler;  // NavHandlerのインスタンスを引数として受け取り保持
        this.popupQryS = document.querySelector(".popup");
        this.overlayQryS = document.querySelector(".overlay");
        this.COUNT_DOWN_RELOAD = 1200;
        this.init();
    }

    init() {
        this.setup_event_listeners();
    }

    showSigninForm(){
        this.popupQryS.innerHTML = `
            <div class=decorator-bar></div>
            <button class="close-button"></button>
            <div class="signpop">
                <h3>登入會員帳號</h3>
                <form class="signpop__form">
                    <label for="email"></label>
                    <input type="email" id="email" name="email" required placeholder="輸入電子信箱">
                    <label for="password"></label>
                    <input type="password" id="password" name="password" required placeholder="輸入密碼">
                    <button type="submit">登入帳戶</button>
                </form>
                <p class="res-text"></p>
                <p>還沒有帳戶 ? <span class="signpop__toggle">點此註冊</span></p>
            </div>
        `;
        document.querySelector(".signpop__toggle").addEventListener("click", this.showSignupForm.bind(this));
        document.querySelector(".signpop__form").addEventListener("submit", this.handleSignin.bind(this));
        document.querySelector(".close-button").addEventListener("click", this.closePopup.bind(this));
    }

    showSignupForm(){
        this.popupQryS.innerHTML = `
            <div class=decorator-bar></div>
            <button class="close-button"></button>
            <div class="signpop">
                <h3>註冊會員帳號</h3>
                <form class="signpop__form">
                    <label for="name"></label>
                    <input type="text" id="name" required placeholder="輸入姓名">
                    <label for="new-email"></label>
                    <input type="email" id="new-email" required placeholder="輸入電子郵件">
                    <label for="new-password"></label>
                    <input type="password" id="new-password" required placeholder="輸入密碼">
                    <button type="submit">註冊新帳戶</button>
                </form>
                <p class="res-text"></p>
                <p>已經有帳戶了 ? <span class="signpop__toggle">點此登入</p>
            </div>
        `;
        document.querySelector(".signpop__toggle").addEventListener("click", this.showSigninForm.bind(this));
        document.querySelector(".signpop__form").addEventListener("submit", this.handleSignup.bind(this));
        document.querySelector(".close-button").addEventListener("click", this.closePopup.bind(this));
    }

    async setJwtAfterChecked(emailArg, pswArg){
        const email = document.getElementById(emailArg).value;
        const psw = document.getElementById(pswArg).value;
        const jsonData = await fetchResponseJson("PUT", "/api/user/auth", {email: email, password: psw})
        if (jsonData.error) {
            this.responseColorText(jsonData.message, false);
        } else {
            const token = jsonData.token;
            localStorage.setItem("jwtoken", token);   // LocalStorageにJWTを保存
            return true;
        }
    }

    async handleSignin(event){
        event.preventDefault();
        const hasJwt = await this.setJwtAfterChecked("email", "password");
        if (hasJwt) {
            this.responseColorText("登入成功", true);
            this.navHandler.renderNavSignin();
            await new Promise(resolve => setTimeout(() => {
                this.navHandler.checkUserStatusByjwt();       // window.location.reload();　　//整個畫面都reflesh會下降UX
                this.closePopup();
                resolve();
            }, this.COUNT_DOWN_RELOAD));
        }
    }

    async handleSignup(event){
        event.preventDefault();
        const name = document.getElementById("name").value;
        const email = document.getElementById("new-email").value;
        const psw = document.getElementById("new-password").value;
        const jsonData = await fetchResponseJson("POST", "/api/user", {name: name, email: email, password: psw})
        if (jsonData.error) {
            this.responseColorText(jsonData.message, false);
        } else {
            this.responseColorText("註冊成功", true);
            await new Promise(resolve => setTimeout(async () => {
                const hasJwt = await this.setJwtAfterChecked("new-email", "new-password");
                if (hasJwt) {
                    this.navHandler.renderNavSignin();
                    window.location.reload();   //整個畫面都reflesh會下降UX
                    resolve();
                }
            }, this.COUNT_DOWN_RELOAD));
        }
    }

    closePopup(){
        this.popupQryS.classList.remove("active");
        this.overlayQryS.classList.remove("active");
    }

    responseColorText(message, isSuccess) {
        const resTextQryS = document.querySelector(".res-text");
        if (resTextQryS) {
            resTextQryS.textContent = message;
            if (isSuccess) {
                resTextQryS.classList.add("res-text--success");
                resTextQryS.classList.remove("res-text--failure");
            } else {
                resTextQryS.classList.add("res-text--failure");
                resTextQryS.classList.remove("res-text--success");
            }
        }
    }

    setup_event_listeners() {
        this.navSignpopQryS.addEventListener("click", () => {
            this.showSigninForm();
            this.popupQryS.classList.add("active");
            this.overlayQryS.classList.add("active");
        })

        this.overlayQryS.addEventListener("click", () => {
            this.closePopup();
        })
    }
}


class NavHandler {   //責務はnavの処理
    constructor(qryS) {    //インスタンス化した際の引数を受けれる
        this.navSignpopQryS = document.querySelector(qryS);
        this.signPopup = null;  //newで呼び出す前に必ず定義されてること
    }

    async checkUserStatusByjwt() {
        const jsonData = await fetchResponseBearer("/api/user/auth");
        if (!jsonData.data) {  //!==nullにしないのは、throw Errorされるとundefinedが返されこれに対応する為
            this.renderNavSignout();
        } else {
            this.renderNavSignin();
        }
    }

    renderNavSignin() {  //signin成功時の処理の為popupに記述の方が相応しい
        this.navSignpopQryS.textContent = "登出系統";
        if (this.signPopup) {
            this.navSignpopQryS.removeEventListener("click", this.signPopup.showSigninForm.bind(this.signPopup)); //削除の際はbind不要
        }
        this.navSignpopQryS.addEventListener("click", this.handleSignout.bind(this));
    }

    renderNavSignout() {
        this.navSignpopQryS.textContent = "登入/註冊";
        this.navSignpopQryS.removeEventListener("click", this.handleSignout.bind(this));
        if (!this.signPopup) {
            this.signPopup = new SignPopup(this.navSignpopQryS, this);
        }
        this.navSignpopQryS.addEventListener("click", this.signPopup.showSigninForm.bind(this.signPopup));
    }

    handleSignout() {
        localStorage.removeItem("jwtoken");
        this.renderNavSignout();
        window.location.reload();   //整個畫面都reflesh會下降UX
    }
}

export const navHandler = new NavHandler(".nav__signpop");  //newで呼び出す前に必ず定義されてること
