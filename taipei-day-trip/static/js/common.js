/* moduleを使うには、『呼び出したいファイル』の<script>タグにtype="module"属性を追加する必要あり */
export async function fetchResponseJson(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {    // 200番以外の時にError, but200番で空の場合はNot Error
            throw new Error(`HTTP Error! status: ${response.status}`);
        }
        const jsonData = await response.json();
        return jsonData;
    } catch (error) {
        console.error("Fetch Error", error);
    }
}

export const preloadImage = (url) => {
    const link = document.createElement("link");
    link.rel = "preload";
    link.href = url;
    link.as = "image";
    document.head.appendChild(link);
}

export function createElmAndClass(elm, className) {
    const element = document.createElement(elm);
    element.classList.add(className);      // classList.addの戻り値はundefinedの為, createElementと一緒に書けない。
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

    const updateImage = (mode) => {
        imgElm.src = mode === "dark" ? "/static/images/icons/mode-dark32x32.webp" : "/static/images/icons/mode-light32x32.webp";
    }

    btnDark.addEventListener("click", () => {
        const modeNow = document.documentElement.getAttribute("data-theme");
        const updateMode = modeNow === "dark" ? "light" : "dark";     //trueならlightに、falseならdarkに
        document.documentElement.setAttribute("data-theme", updateMode);
        updateImage(updateMode);
    })
    const initialMode = document.documentElement.getAttribute("data-theme");
    updateImage(initialMode);
}

export function jump2Top() {
    const toTopBtn = document.querySelector(".jump2top-btn");
    const imgElm = document.createElement("img");
    imgElm.alt = "jump-btn";
    imgElm.src = "/static/images/icons/to-top96x96.webp";
    toTopBtn.appendChild(imgElm);

    let isScrolling;
    window.addEventListener("scroll", () => {
        toTopBtn.style.display = "block";
        clearTimeout(isScrolling);
        isScrolling = setTimeout(() => {
            toTopBtn.style.display = "none";
        }, 1200);
    })
    toTopBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    })
}

//JWTをheaderに含めてリクエストを送信
export async function checkUserStatusByjwt(){
    const token = localStorage.getItem("jwtoken");
    try {
        const response = await fetch("/api/user/auth", {
            method: "GET",   // APIリクエストのヘッダーにJWTを含める
            headers: { "Authorization": `Bearer ${token}`}
        });
        if (!response.ok) {    // 200番以外の時にError, but200番で空の場合はNot Error
            throw new Error(`HTTP Error! status: ${response.status}`);
        }
        const jsonData = await response.json();
        if(jsonData.data) {
            renderNavSignin();
        } else {
            renderNavSignout();
        }
    } catch(error) {
        console.error("Fetch Error", error);
    }
}

function renderNavSignin(){
    document.querySelector(".nav__signpop").textContent = "登出系統";
    document.querySelector(".nav__signpop").removeEventListener("click", createPopupSignin);
    document.querySelector(".nav__signpop").addEventListener("click", handleSignout);
}

function renderNavSignout(){
    document.querySelector(".nav__signpop").textContent = "登入/註冊";
    document.querySelector(".nav__signpop").removeEventListener("click", handleSignout);
    document.querySelector(".nav__signpop").addEventListener("click", createPopupSignin);
}

function handleSignout(){
    localStorage.removeItem("jwtoken");    //logout時にjwtを削除
    renderNavSignout();
    window.location.reload();   //整個畫面都reflesh會下降UX
}


//pop-up signup/in
export function createPopupSignin(){
    const popupQryS = document.querySelector(".popup");
    const overlayQryS = document.querySelector(".overlay");

    document.querySelector(".nav__signpop").addEventListener("click", function(){
        showLoginForm();
        popupQryS.classList.add("active");
        overlayQryS.classList.add("active");
    })

    overlayQryS.addEventListener("click", function(){
        popupQryS.classList.remove("active");
        overlayQryS.classList.remove("active");
    })

    function showLoginForm(){
        popupQryS.innerHTML = `
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
        document.querySelector(".signpop__form").addEventListener("submit", handleSignin);
        document.querySelector(".signpop__toggle").addEventListener("click", showSignupForm);
        document.querySelector(".close-button").addEventListener("click", closeBtn);
    }

    function showSignupForm(){
        popupQryS.innerHTML = `
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
        document.querySelector(".signpop__form").addEventListener("submit", handleSignup);
        document.querySelector(".signpop__toggle").addEventListener("click", showLoginForm);
        document.querySelector(".close-button").addEventListener("click", closeBtn);
    }

    async function fetchSignin(emailArg, pswArg){
        const email = document.getElementById(emailArg).value;
        const password = document.getElementById(pswArg).value;
        try {   // loginリクエストの送信(jwtがreturnされる)
            const response = await fetch("/api/user/auth", {
                method: "PUT",
                headers: { "Content-Type": "application/json"},
                body: JSON.stringify({ email: email, password: password})
            });
            if (!response.ok) {    // 200番以外の時にError, but200番で空の場合はNot Error
                throw new Error(`HTTP Error! status: ${response.status}`);
            }
            const jsonData = await response.json();
            return jsonData;
        } catch(error) {
            console.error("Fetch Error", error);
        }
    }

    async function handleSignin(event){
        event.preventDefault();
        const jsonData = await fetchSignin("email", "password");
        if (jsonData.error) {
            responseColorText(".res-text", jsonData.message, false);
        } else {
            const token = jsonData.token;
            localStorage.setItem("jwtoken", token);    // LocalStorageにJWTを保存
            responseColorText(".res-text", "登入成功", true);
            renderNavSignin();
            await new Promise(resolve => setTimeout(() => {
                checkUserStatusByjwt();       // window.location.reload();　　//整個畫面都reflesh會下降UX
                popupQryS.classList.remove("active");
                overlayQryS.classList.remove("active");
                resolve();
            }, 1200));
        }
    }

    async function handleSignup(event){
        event.preventDefault();
        const name = document.getElementById("name").value;
        const email = document.getElementById("new-email").value;
        const password = document.getElementById("new-password").value;
        try {
            const response = await fetch("/api/user", {
                method: "POST",
                headers: { "Content-Type": "application/json"},
                body: JSON.stringify({ name: name, email: email, password: password})
            });
            if (!response.ok) {    // 200番以外の時にError, but200番で空の場合はNot Error
                throw new Error(`HTTP Error! status: ${response.status}`);
            }
            const jsonData = await response.json();
            if (jsonData.error) {
                responseColorText(".res-text", jsonData.message, false);
                throw new Error("signUp Fetch Error", error);
            }
            responseColorText(".res-text", "註冊成功", true);
            await new Promise(resolve => setTimeout(async function(){
                const jsonData = await fetchSignin("new-email", "new-password");
                if (jsonData.error) {
                    responseColorText(".res-text", jsonData.message, false);
                    throw new Error("signIn Fetch Error", error);
                }
                const token = jsonData.token;
                localStorage.setItem("jwtoken", token);   // LocalStorageにJWTを保存
                renderNavSignin();
                window.location.reload();   //整個畫面都reflesh會下降UX
                resolve();
            }, 1200));
        } catch(error) {
            console.error("Fetch Error", error);
        }
    }

    function closeBtn(){
        popupQryS.classList.remove('active');
        overlayQryS.classList.remove('active');
    }

    function responseColorText(selector, message, isSuccess) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = message;
            if (isSuccess) {
                element.classList.add("res-text--success");
                element.classList.remove("res-text--failure");
            } else {
                element.classList.add("res-text--failure");
                element.classList.remove('res-text--success');
            }
        }
    }
}