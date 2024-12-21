var searchBtn = document.getElementById("search-button");

function searchquery() {
    // select classification-select
    var classificationSelect = document.getElementById("classification-select");
    var classification = classificationSelect.options[classificationSelect.selectedIndex].value;
    // select status-select
    var statusSelect = document.getElementById("status-select");
    var status = statusSelect.options[statusSelect.selectedIndex].value;
    // input search-input
    var searchInput = document.getElementById("search-input").value;
    // 发送请求 "/laws/" GET ?参数 classification, status, searchInput
    var url = "/laws/?classification=" + classification + "&status=" + status + "&q=" + searchInput;
    window.location.href = url; // 跳转页面
}

searchBtn.addEventListener("click", searchquery);

function keyup_submit(e) {
    var evt = window.event || e;
    if (evt.keyCode == 13) {
        //回车事件
        searchquery();
    }
}