odoo.define("quan_ly_tai_chinh.ai_chat_widget", function (require) {
    "use strict";
    var rpc = require("web.rpc");

    function esc(s) {
        return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    function build() {
        if (document.getElementById("qltc_ai_btn")) return;

        var btn = document.createElement("div");
        btn.id = "qltc_ai_btn";
        btn.title = "Tro ly AI (Gemini)";
        btn.textContent = "🤖";
        document.body.appendChild(btn);

        var panel = document.createElement("div");
        panel.id = "qltc_ai_panel";
        panel.innerHTML =
            '<div id="qltc_ai_head"><span>Trợ lý AI (Gemini)</span>' +
            '<span id="qltc_ai_close">&times;</span></div>' +
            '<div id="qltc_ai_msgs"></div>' +
            '<div id="qltc_ai_inputbar">' +
            '<input id="qltc_ai_input" type="text" placeholder="Nhập câu hỏi..."/>' +
            '<button id="qltc_ai_send" type="button">Gửi</button>' +
            "</div>";
        document.body.appendChild(panel);

        var msgs = panel.querySelector("#qltc_ai_msgs");
        var input = panel.querySelector("#qltc_ai_input");

        function addMsg(text, who) {
            var d = document.createElement("div");
            d.className = "qltc_ai_msg qltc_ai_" + who;
            d.innerHTML = esc(text).replace(/\n/g, "<br/>");
            msgs.appendChild(d);
            msgs.scrollTop = msgs.scrollHeight;
            return d;
        }

        addMsg("Xin chào! Hỏi tôi về tài sản, khấu hao, mua sắm linh kiện, chi phí bảo trì...", "bot");

        function send() {
            var q = (input.value || "").trim();
            if (!q) { return; }
            addMsg(q, "user");
            input.value = "";
            var loading = addMsg("Đang suy nghĩ...", "bot");
            rpc.query({ route: "/quan_ly_tai_chinh/ai_ask", params: { question: q } }).then(
                function (r) {
                    var a = (r && r.answer) ? r.answer : "(khong co phan hoi)";
                    loading.innerHTML = esc(a).replace(/\n/g, "<br/>");
                    msgs.scrollTop = msgs.scrollHeight;
                },
                function () {
                    loading.textContent = "Loi ket noi, thu lai.";
                }
            );
        }

        panel.querySelector("#qltc_ai_send").addEventListener("click", send);
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter") { send(); }
        });
        panel.querySelector("#qltc_ai_close").addEventListener("click", function () {
            panel.style.display = "none";
        });
        btn.addEventListener("click", function () {
            panel.style.display = (panel.style.display === "flex") ? "none" : "flex";
            if (panel.style.display === "flex") { input.focus(); }
        });
    }

    $(function () {
        try { build(); } catch (e) { console.error("AI widget error:", e); }
    });
});
