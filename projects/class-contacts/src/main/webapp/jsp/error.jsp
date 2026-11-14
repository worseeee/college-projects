<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" isErrorPage="true" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>系统出错啦</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body style="background:#fff; text-align:center; padding-top:100px;">
    <div style="font-size:50px; margin-bottom:20px;">😵</div>
    <h3 style="color:#333; margin-bottom:10px;">糟糕，服务器开小差了！</h3>
    <p style="color:#999; font-size:13px; margin-bottom:30px;">
        错误信息: <%= exception != null ? exception.getMessage() : "未知异常" %>
    </p>
    <a href="${pageContext.request.contextPath}/login" class="btn" style="display:inline-block; width:150px; text-decoration:none;">返回安全区</a>
</body>
</html>