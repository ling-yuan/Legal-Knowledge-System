// button id=send-btn
const sendBtn = document.getElementById('send-btn');

// click event
sendBtn.addEventListener('click', async () => {
    const resp = await fetch("/api/chat/", {
        method: 'GET'
    });
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();

    var text = "";
    const container = document.getElementById('chat-container');
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
