<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>登录 - 班级通讯录</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body style="background-color: #ffffff;">

    <div class="header">班级通讯录系统</div>

    <div class="form-container" style="margin-top: 50px;">
        <h2 style="margin-bottom: 30px; text-align: center;">欢迎回来</h2>
        
        <% if(request.getAttribute("errorMsg") != null) { %>
            <div style="color: red; margin-bottom: 15px; font-size: 13px; text-align: center;">
                <%=request.getAttribute("errorMsg")%>
            </div>
        <% } %>

        <form action="${pageContext.request.contextPath}/login" method="post">
            <div class="form-group">
                <input type="text" name="username" placeholder="请输入学号/用户名" 
                       value="${requestScope.inputUsername}" required>
            </div>
            <div class="form-group">
                <input type="password" name="password" placeholder="请输入密码" required>
            </div>
            <button type="submit" class="btn">登 录</button>
        </form>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="${pageContext.request.contextPath}/register" style="color: var(--primary-color); text-decoration: none;">没有账号？立即注册</a>
        </div>
    </div>

</body>
</html>