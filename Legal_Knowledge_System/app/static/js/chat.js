// button id=send-btn
const sendBtn = document.getElementById('send-button');

// click event
sendBtn.addEventListener('click', async () => {
    const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    var question = document.getElementById('message-input').value;
    console.log(question);
    // 构造请求
    const req = new Request("/api/chat/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "question": question
        })
    })
    // 发送请求
    const resp = await fetch(req);

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();

    var text = "";

    // 将默认界面隐藏
    document.getElementById('default').style.display = 'none';
    const container = document.getElementById('messages');
    const div = document.createElement('div');
    container.appendChild(div);
    while (true) {
        const {
            done,
            value
        } = await reader.read();

        if (done) break;

        text += decoder.decode(value);

        console.log(done, text);
        div.innerHTML = marked.parse(text);
    }
    container.scrollTop = container.scrollHeight;
})
