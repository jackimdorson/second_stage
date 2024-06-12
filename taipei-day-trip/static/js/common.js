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