// button id=send-btn
const sendBtn = document.getElementById('send-btn');
function add_element(txt) {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.innerText = txt;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// click event
sendBtn.addEventListener('click', async () => {
    const resp = await fetch("/api/chat/", {
        method: 'GET'
    });
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const {
            done,
            value
        } = await reader.read();

        if (done) break;

        const txt = decoder.decode(value);

        console.log(done);
        console.log(txt);
        add_element(txt);
    }
})
