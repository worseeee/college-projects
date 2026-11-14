<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>消息中心</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
    <style>
        .badge { background:#fa5151; color:#fff; font-size:11px; padding:2px 6px; border-radius:10px; font-weight:bold; }
    </style>
</head>
<body>
    <div class="header">消息大厅</div>
    
    <div class="contact-list" style="padding-bottom:80px;">
        <c:if test="${empty sessionChats}">
            <div style="text-align:center; color:#999; margin-top:100px; font-size:15px;">
                💬 暂无私聊会话<br><span style="font-size:12px;color:#ccc;">去通讯录找同学发起聊天吧！</span>
            </div>
        </c:if>
        
        <c:forEach items="${sessionChats}" var="chat">
            <a href="${pageContext.request.contextPath}/message?action=chat&targetId=${chat.senderId == sessionUser.id ? chat.receiverId : chat.senderId}" 
               class="contact-card" style="text-decoration:none; color:inherit; display:flex; align-items:center;">
               
                <%-- 1. 修复头像：使用 targetAvatar，显示聊天伙伴的头像 --%>
                <img class="user-avatar avatar-contact-sm me-3" 
                     src="${pageContext.request.contextPath}/avatar/${empty chat.targetAvatar ? 'default.png' : chat.targetAvatar}" 
                     alt="用户头像" 
                     onerror="this.src='${pageContext.request.contextPath}/images/default.png'"/>
                     
                <div class="contact-info" style="flex:1; overflow:hidden;">
                    <div class="contact-name" style="display:flex; justify-content:space-between; align-items:center;">
                        <%-- 2. 修复姓名：使用 targetName --%>
                        <span>${chat.targetName}</span>
                        <span style="font-size:11px; color:#999; font-weight:normal;">
                            <fmt:formatDate value="${chat.createTime}" pattern="MM-dd HH:mm"/>
                        </span>
                    </div>
                    <div style="font-size:13px; color:#888; margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        ${chat.content}
                    </div>
                </div>
                
                <%-- 微信级数字未读气泡引擎 --%>
                <c:if test="${chat.unreadCount > 0}">
                    <div style="margin-left:10px;">
                        <span class="badge" style="padding: 2px 7px; border-radius: 12px; box-shadow: 0 2px 4px rgba(250,81,81,0.3);">
                            ${chat.unreadCount > 99 ? '99+' : chat.unreadCount}
                        </span>
                    </div>
                </c:if>
            </a>
        </c:forEach>
    </div>

    <jsp:include page="/jsp/tabbar.jsp" />
</body>
</html>