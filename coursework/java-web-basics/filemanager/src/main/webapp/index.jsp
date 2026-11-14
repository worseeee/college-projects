<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>文件上传与下载管理系统</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        
        <div class="section-title">文件上传</div>
        <div class="card">
            <form action="upload" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label>用户名：</label>
                    <input type="text" name="username" class="form-control" 
                           value="${sessionScope.currentUsername}" placeholder="请输入用户名" required>
                </div>
                <div class="form-group">
                    <label>选择文件：</label>
                    <input type="file" name="file" class="form-control" required>
                </div>
                <button type="submit" class="btn-upload btn-success">上传文件</button>
            </form>
        </div>

        <div class="section-title">文件下载</div>
        <div class="card">
            <jsp:include page="fileList.jsp"></jsp:include>
        </div>
        
    </div>
</body>
</html>