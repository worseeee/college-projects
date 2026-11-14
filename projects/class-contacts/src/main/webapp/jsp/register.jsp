<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>用户注册 - 班级通讯录</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body style="background-color: #ffffff;">

    <div class="header">新同学注册</div>

    <div class="form-container" style="margin-top: 20px;">
        
        <% if(request.getAttribute("errorMsg") != null) { %>
            <div style="color: #e74c3c; background: #fadbd8; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 13px; text-align: center;">
                <%=request.getAttribute("errorMsg")%>
            </div>
        <% } %>

        <form action="${pageContext.request.contextPath}/register" method="post">
            <div class="form-group">
                <input type="text" name="studentNo" placeholder="请输入学号 (必填，唯一)" required>
            </div>
            <div class="form-group">
                <input type="text" name="username" placeholder="请输入登录账号 (必填，唯一)" required>
            </div>
            <div class="form-group">
                <input type="password" name="password" placeholder="请输入密码 (必填)" required>
            </div>
            <div class="form-group">
                <input type="text" name="realName" placeholder="请输入真实姓名 (必填)" required>
            </div>
            <div class="form-group">
                <input type="tel" name="phone" placeholder="请输入手机号码 (必填)" required>
            </div>
            <div class="form-group">
                <input type="email" name="email" placeholder="请输入电子邮箱 (选填)">
            </div>
            
            <button type="submit" class="btn">立即注册</button>
        </form>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="${pageContext.request.contextPath}/login" style="color: var(--text-muted); text-decoration: none; font-size: 13px;">已有账号？返回登录</a>
        </div>
    </div>

</body>
</html>