<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.ArrayList" %>
<%@ page import="java.util.List" %>
<%
    // 1. 设置请求和响应的编码，防止中文乱码
    request.setCharacterEncoding("UTF-8");
    response.setCharacterEncoding("UTF-8");

    // 2. 初始化全局聊天记录（如果 application 中没有，则创建一个空的 List）
    List<String> chatHistory = (List<String>) application.getAttribute("chatHistory");
    if (chatHistory == null) {
        chatHistory = new ArrayList<String>();
        application.setAttribute("chatHistory", chatHistory);
    }

    // 3. 处理表单提交动作
    String action = request.getParameter("action");
    if ("send".equals(action)) {
        String username = request.getParameter("username");
        String message = request.getParameter("message");

        // 如果用户输入了内容
        if (username != null && !username.trim().isEmpty() && message != null && !message.trim().isEmpty()) {
            // 将用户名存入 session，下次访问就不用重填了
            session.setAttribute("currentUser", username);
            
            // 拼装消息并加入到全局 application 中
            String record = "[" + username + "] 说: " + message;
            chatHistory.add(record);
            
            // 为了防止用户按 F5 刷新页面导致表单重复提交，采用重定向 (PRG 模式)
            response.sendRedirect("chat.jsp");
            return; // 重定向后必须 return，停止执行后面的 HTML 渲染
        }
    } else if ("clear".equals(action)) {
        // 附加功能：清空聊天记录
        chatHistory.clear();
        response.sendRedirect("chat.jsp");
        return;
    }

    // 4. 获取 session 中的用户名，用于回显表单
    String defaultUser = (String) session.getAttribute("currentUser");
    if (defaultUser == null) defaultUser = "";
%>
<!DOCTYPE html>
<html>
<head>
    <title>JSP 简易聊天室</title>
    <style>
        body { font-family: "Microsoft YaHei"; background: #f0f2f5; padding: 20px; }
        .chat-container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .chat-box { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin-bottom: 15px; background: #fafafa; }
        .msg-item { padding: 5px; border-bottom: 1px dashed #eee; }
        .form-group { margin-bottom: 10px; }
        input[type="text"] { padding: 8px; width: 70%; border: 1px solid #ccc; border-radius: 4px; }
        .user-input { width: 120px !important; }
        button { padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn-clear { background: #dc3545; }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2>公共聊天室</h2>
        
        <div class="chat-box" id="chatBox">
            <% 
                // 遍历 application 中的聊天记录并输出
                if(chatHistory.isEmpty()){
                    out.print("<p style='color:#999;'>暂无聊天记录，来发第一条消息吧！</p>");
                } else {
                    for(String msg : chatHistory) {
                        out.print("<div class='msg-item'>" + msg + "</div>");
                    }
                }
            %>
        </div>

        <form action="chat.jsp" method="post">
            <input type="hidden" name="action" value="send">
            <div class="form-group">
                <label>姓名：</label>
                <input type="text" name="username" class="user-input" value="<%= defaultUser %>" required>
            </div>
            <div class="form-group">
                <label>内容：</label>
                <input type="text" name="message" required autocomplete="off" placeholder="请输入聊天内容...">
                <button type="submit">发送消息</button>
            </div>
        </form>
        
        <form action="chat.jsp" method="post" style="margin-top: 10px;">
            <input type="hidden" name="action" value="clear">
            <button type="submit" class="btn-clear">清空聊天大厅</button>
        </form>
    </div>

    <script>
        var chatBox = document.getElementById("chatBox");
        chatBox.scrollTop = chatBox.scrollHeight;
    </script>
</body>
</html>