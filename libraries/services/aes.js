// Load CryptoJS library
var script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js';
document.head.appendChild(script);

function Call(appID, sessionID, secureKey, board_id, score, async=1)
{
    // build the input object
    const call = EncryptCall({component: 'ScoreBoard.postScore', parameters: {id: board_id, value: score}}, secureKey);
    const input = 
    {
        app_id: appID,
        session_id: sessionID,
        call
    };

    // build post data
    const formData = new FormData();
    formData.append('input', JSON.stringify(input));
    
    // send post data
    const xmlHttp = new XMLHttpRequest();
    const url = 'https://newgrounds.io/gateway_v3.php';
    xmlHttp.open('POST', url, async);
    xmlHttp.send(formData);
    
    if (xmlHttp.responseText)
    {
        console.log(xmlHttp.responseText);

        responseText = xmlHttp.responseText;
        return JSON.parse(xmlHttp.responseText);
    }
}
    
function EncryptCall(call, key)
{
    // encrypt using AES-128 Base64 with CryptoJS
    const aesKey = CryptoJS.enc.Base64.parse(key);
    const iv = CryptoJS.lib.WordArray.random(16);
    const encrypted = CryptoJS.AES.encrypt(JSON.stringify(call), aesKey, {iv});
    const secure = CryptoJS.enc.Base64.stringify(iv.concat(encrypted.ciphertext));

    call.secure = secure;
    call.parameters = null;
    return call;
}