// button id=send-btn
const sendBtn = document.getElementById('send-button');
const clearHistoryBtn = document.getElementById('clear-history');
const messages_box = document.getElementById('messages')
const default_message = document.getElementById('default')

/**
 * 创建消息元素
 * @param {boolean} is_user 是否为用户消息
 * @returns {Element} 消息元素
 */
function create_message(is_user) {
    // 将默认界面隐藏
    default_message.style.display = 'none';
    // 获取聊天容器
    const container = document.getElementById('messages');
    // 创建用户元素
    const div = document.createElement('div');
    // 添加类名
    div.classList.add(is_user ? 'user' : 'bot');

    // 创建消息元素
    const message = document.createElement('div');
    message.classList.add('markdown-body');
    message.classList.add('message');
    // 添加到聊天容器中
    container.appendChild(div);
    div.appendChild(message);
    return message;
}

/**
 * 将文本转换为消息元素并添加到聊天容器中
 * @param {Element} elem 消息容器
 * @param {string} text 消息文本
 * */
function flush_message(elem, text) {
    elem.innerHTML = marked.parse(text);
    elem.parentElement.scrollIntoView({ behavior: "smooth", block: "end" });
}

// click event
sendBtn.addEventListener('click', async () => {
    // 获取输入框内容
    var question = document.getElementById('message-input').value;
    // 清空输入框
    document.getElementById('message-input').value = '';
    // 创建用户消息元素
    const el_user_message = create_message(true);
    // 将用户消息添加到聊天容器中
    flush_message(el_user_message, question);

    // 获取csrf token
    const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
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

    // 获取响应内容
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();

    // 创建bot消息元素
    const el_bot_message = create_message(false);
    // 将bot消息添加到聊天容器中
    flush_message(el_bot_message, "正在思考中...");
    // 读取响应内容
    var text = "";
    while (true) {
        const {
            done,
            value
        } = await reader.read();

        if (done) break;

        text += decoder.decode(value);

        // 更新bot消息内容
        flush_message(el_bot_message, text);
    }
    container.scrollTop = container.scrollHeight;
});

// clear history
clearHistoryBtn.addEventListener('click', async () => {
    // 获取csrf token
    const csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    // 构造请求
    const req = new Request("/api/chat/history/clear/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    // 发送请求
    await fetch(req);
    // 清空聊天容器
    messages_box.innerHTML = '';
    // 显示默认界面
    default_message.style.display = 'flex';
    messages_box.appendChild(default_message);
});

(function () {
    // 查找class中包含history的元素
    const history = document.getElementsByClassName('history');
    // 如果存在history元素
    if (history.length > 0) {
        // 隐藏默认界面
        default_message.style.display = 'none';
        // 遍历history元素
        Array.from(history).forEach(elem => {
            // 获取子节点
            const child = elem.children[0];
            // 获取文本内容
            const text = child.innerText;
            // 渲染文本内容
            flush_message(child, text);
        });
    } else {
        // 显示默认界面
        default_message.style.display = 'flex';
        messages_box.appendChild(default_message);
    }
})();