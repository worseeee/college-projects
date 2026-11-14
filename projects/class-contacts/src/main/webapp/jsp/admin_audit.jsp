<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新生注册审核</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body>
    <div class="header">后台管理 - 注册审核</div>
    <div class="contact-list" style="margin-top: 10px;">
        <c:if test="${empty pendingUsers}">
            <div style="text-align:center; color:#999; margin-top:50px;">暂无待审核的新生</div>
        </c:if>
        
        <c:forEach items="${pendingUsers}" var="user">
            <div class="contact-card">
                <div class="contact-info">
                    <div class="contact-name">${user.realName} <span style="font-size:12px;color:#666;">(${user.studentNo})</span></div>
                    <div class="contact-tags"><span style="background:#fff3cd;color:#856404;">待审核</span></div>
                </div>
                <div class="contact-action" style="display: flex; gap: 5px;">
                    <form action="audit" method="post" style="margin:0;">
                        <input type="hidden" name="userId" value="${user.id}">
                        <input type="hidden" name="actionStatus" value="1">
                        <button type="submit" style="background:#07c160; color:#fff; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">通过</button>
                    </form>
                    <form action="audit" method="post" style="margin:0;">
                        <input type="hidden" name="userId" value="${user.id}">
                        <input type="hidden" name="actionStatus" value="2">
                        <button type="submit" style="background:#e74c3c; color:#fff; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">拒绝</button>
                    </form>
                </div>
            </div>
        </c:forEach>
        <div style="text-align: center; margin-top: 20px;">
            <a href="${pageContext.request.contextPath}/contacts" style="color: var(--primary-color);">返回大厅</a>
        </div>
    </div>
</body>
</html>