<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>上传结果</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container" style="width: 400px; text-align: center; margin-top: 100px;">
        <div class="card">
            
            <%-- 使用 EL 表达式判断上传状态 --%>
            <div class="${status == 'success' ? 'alert-success' : 'alert-error'}">
                <h3>${msg}</h3>
            </div>
            
            <a href="index.jsp" class="btn-upload" style="display:inline-block; text-decoration:none; margin-top: 20px; width: auto; padding: 10px 30px;">返回系统首页</a>
        </div>
    </div>
</body>
</html>