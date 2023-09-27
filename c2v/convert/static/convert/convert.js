function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
function submitConvertDo(e) {
  if (e) e.preventDefault(); // 元のsubmitをキャンセル
  // urlsが未入力の場合アラートメッセージ出してリターン
  let urls = document.getElementsByName("urls")[0].value;
  if (!urls.replaceAll("\n", "").trim()) {
    document.getElementsByName("warn")[0].textContent = "絶対入力してくらさい！";
    document.getElementsByName("warn")[0].classList.replace("d-none", "d-block");
    return;
  }
  const xhr = new XMLHttpRequest();
  
  const fd = new FormData();
  let site = "";
  ["site", "aca", "pass"].forEach((key) => {
    let val = document.getElementsByName(key)[0].value;
    fd.append(key, val);
    if (key=='site') site = val;
    else localStorage.setItem(`${site}_${key}`, val);
  });
  let trimedUrls = { submit: "", next: "" };
  urls.split("\n").forEach((u) => {
    let ut = u.trim();
    if (ut) {
      if (!trimedUrls.submit) trimedUrls.submit = ut;
      else {
        if (trimedUrls.next) trimedUrls.next += "\n";
        trimedUrls.next += ut;
      }
    }
  });

  fd.append("url", trimedUrls.submit);
  document.getElementsByName("urls")[0].value = trimedUrls.next;

  let stdoutBox = document.querySelector("#stdout");
  stdoutBox.innerHTML = ""; // 空欄に初期化
  stdoutBox.classList.replace("d-none", "d-block");
  let dUrlBlock = document.querySelector("#d-url");
  let dUrl = document.querySelector("#d-url>span");
  dUrlBlock.classList.replace("d-none", "d-block");
  dUrl.textContent = trimedUrls.submit;

  console.log(...fd.entries());
  xhr.open("POST", "do/");
  xhr.setRequestHeader("X-CSRFToken", csrftoken); // csrftokenをくっつけます
  xhr.onreadystatechange = function () {
    if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
      // 正常に受信完了した時の処理
      const d = this.response; // これで帰ってきたデータを取り出せます
      stdoutBox.innerHTML = d;
      stdoutBox.scrollTo(0, stdoutBox.scrollHeight);
      // console.log(d);
      let fLine = d.split("<br />").filter((f) => f.indexOf("[download] Destination:") > -1)[0];
      let fName = fLine.replace("[download] Destination:", "").trim();
      download(fName);
    } else if (this.readyState !== XMLHttpRequest.DONE && this.status === 200) {
      let d = this.response; // これで帰ってきたデータを取り出せます
      // console.log("途中", d);
      stdoutBox.innerHTML = d;
      stdoutBox.scrollTo(0, stdoutBox.scrollHeight);
    }
  };
  xhr.send(fd); // この時点で送信されます
}
function download(fName) {
  const xhr = new XMLHttpRequest();
  let encFname = "download/?f_name=" + encodeURIComponent(escapeHtml(fName));
  xhr.open("GET", encFname);
  xhr.responseType = "blob"; //blob型のレスポンスを受け付ける
  xhr.onload = function () {
    if (this.status == 200) {
      var blob = this.response; //レスポンス
      //IEとその他で処理の切り分け
      if (navigator.appVersion.toString().indexOf(".NET") > 0) {
        //IE 10+
        window.navigator.msSaveBlob(blob, fileName + ".pdf");
      } else {
        //aタグの生成
        var a = document.createElement("a");
        //レスポンスからBlobオブジェクト＆URLの生成
        var blobUrl = window.URL.createObjectURL(new Blob([blob], { type: blob.type }));
        //上で生成したaタグをアペンド
        document.body.appendChild(a);
        a.style = "display: none";
        //BlobオブジェクトURLをセット
        a.href = blobUrl;
        //ダウンロードさせるファイル名の生成
        a.download = fName;
        //クリックイベント発火
        a.click();
        fileRemove(fName);
      }
    }
  };
  xhr.send(); // この時点で送信されます
}
function fileRemove(fName) {
  const xhr = new XMLHttpRequest();
  let encFname = "fileRemove/?f_name=" + encodeURIComponent(escapeHtml(fName));
  xhr.open("GET", encFname);
  xhr.onload = function () {
    if (this.status == 200) {
      let urls = document.getElementsByName("urls")[0].value;
      if (urls.replaceAll("\n", "").trim()) {
        submitConvertDo();
      }
    }
  };
  xhr.send(); // この時点で送信されます
}
function changeSite() {
  let site = document.getElementsByName("site")[0].value;
  document.getElementsByName("aca")[0].value = localStorage.getItem(`${site}_aca`);
  document.getElementsByName("pass")[0].value = localStorage.getItem(`${site}_pass`);
}
var escapeHtml = function(str) {
	if (typeof str !== 'string') return str;
	var patterns = {
		'<' : '&lt;', 
    '>' : '&gt;',
		'&' : '&amp;',
		'"' : '&quot;',
    "'" : '&#x27;',
		'`' : '&#x60;'
	};
	return str.replace(/<|>|&|"|'|`/g, function(match) {
		return patterns[match];
	});
};
const csrftoken = getCookie("csrftoken");
const form = document.getElementsByTagName("form");
form[0].addEventListener("submit", submitConvertDo); // submitイベントをオーバライド
const site = document.getElementsByName("site");
site[0].addEventListener("change", changeSite); // submitイベントをオーバライド
site[0].dispatchEvent(new Event("change"))
