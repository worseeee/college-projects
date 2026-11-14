<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>活动中心</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body>
    <div class="header">班级活动报名</div>
    
    <div class="contact-list">
        <c:forEach items="${activities}" var="act">
            <div class="contact-card" style="display:block;">
                <h3 style="margin-bottom:5px;">${act.title}</h3>
                <p style="font-size:13px; color:#666; margin-bottom:10px;">${act.content}</p>
                <p style="font-size:12px; color:#07c160; margin-bottom:10px;">
                    活动时间: <fmt:formatDate value="${act.activityTime}" pattern="yyyy-MM-dd HH:mm"/>
                </p>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:12px; color:#999;">已报名: ${act.enrolledCount} 人</span>
                    <div>
                        <form action="${pageContext.request.contextPath}/activity?action=enroll" method="post" style="display:inline;">
                            <input type="hidden" name="id" value="${act.id}">
                            <button type="submit" style="background:var(--primary-color); color:white; border:none; padding:6px 12px; border-radius:4px;">报名</button>
                        </form>
                        <c:if test="${sessionScope.sessionUser.role == 2}">
                            <a href="${pageContext.request.contextPath}/activity?action=enrollList&id=${act.id}" style="color:#007bff; font-size:13px; margin-left:10px; text-decoration:none;">查看名单</a>
                        </c:if>
                    </div>
                </div>
            </div>
        </c:forEach>
    </div>
</body>
</html>