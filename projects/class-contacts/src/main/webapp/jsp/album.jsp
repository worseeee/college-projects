<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>班级相册</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
    <style>
        .photo-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 10px; }
        .photo-item { background: #fff; padding: 5px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .photo-img { width: 100%; height: 150px; object-fit: cover; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">照片墙</div>
    
    <div style="padding:10px; background:#fff; text-align:center;">
        <form action="${pageContext.request.contextPath}/album?action=upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required style="margin-bottom:10px;">
            <input type="text" name="description" placeholder="写句描述吧..." style="width:100%; padding:8px; border:1px solid #ccc; margin-bottom:10px;">
            <button type="submit" class="btn" style="padding:10px;">上传照片</button>
        </form>
    </div>

    <div class="photo-grid">
        <c:forEach items="${photos}" var="p">
            <div class="photo-item">
                <img src="${pageContext.request.contextPath}/${p.photoUrl}" class="photo-img">
                <div style="font-size:12px; color:#666; margin-top:5px;">${p.description}</div>
                <div style="font-size:11px; color:#999; margin-top:3px;">By: ${p.uploaderName}</div>
                <c:if test="${p.userId == sessionScope.sessionUser.id || sessionScope.sessionUser.role == 2}">
                    <form action="${pageContext.request.contextPath}/album?action=delete" method="post" style="margin-top:5px;">
                        <input type="hidden" name="id" value="${p.id}">
                        <button type="submit" style="background:#ff4d4f; color:#fff; border:none; padding:3px 8px; border-radius:3px; font-size:11px; width:100%;">删除</button>
                    </form>
                </c:if>
            </div>
        </c:forEach>
    </div>
</body>
</html>