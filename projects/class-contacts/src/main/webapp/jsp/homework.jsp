<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>作业中心</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="m-0 font-weight-bold text-dark">📋 班级作业中心</h3>
        <a href="${pageContext.request.contextPath}/contactList" class="btn btn-outline-secondary btn-sm">返回大厅</a>
    </div>

    <c:choose>
        <c:when test="${empty homeworkList}">
            <div class="text-center py-5 bg-white rounded shadow-sm">
                <p class="text-muted m-0">太棒啦！当前没有任何未交作业</p>
            </div>
        </c:when>
        <c:otherwise>
            <c:forEach var="hw" items="${homeworkList}">
                <div class="card shadow-sm mb-3 border-start border-primary border-4">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5 class="card-title text-primary font-weight-bold">${hw.title}</h5>
                            <span class="badge bg-warning text-dark">截止时间: ${hw.deadline}</span>
                        </div>
                        <p class="card-text text-secondary mt-2">${hw.description}</p>
                        <c:if test="${not empty hw.attachment}">
                            <div class="bg-light p-2 rounded d-flex justify-content-between align-items-center mt-3">
                                <span class="small text-truncate text-muted">📎 ${hw.attachment}</span>
                                <a href="${pageContext.request.contextPath}/homework?action=download&filename=${hw.attachment}" 
                                   class="btn btn-sm btn-primary">点击下载附件</a>
                            </div>
                        </c:if>
                    </div>
                </div>
            </c:forEach>
        </c:otherwise>
    </c:choose>
</div>
<%@ include file="tabbar.jsp" %>
</body>
</html>