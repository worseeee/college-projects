<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>班级留言板</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body>
    <div class="header">公共留言板</div>

    <%-- ⚠️ 接收重复点赞的反馈提示条 --%>
    <c:if test="${not empty sessionScope.flashMsg}">
        <div style="background-color: #fff3cd; color: #856404; padding: 10px; text-align: center; font-size: 13px; font-weight: bold; border-bottom: 1px solid #ffeeba;">
            ${sessionScope.flashMsg}
        </div>
        <c:remove var="flashMsg" scope="session"/>
    </c:if>

    <div class="contact-list" style="margin-bottom: 70px;">
        <div class="contact-card" style="display:block; padding: 10px;">
            <form action="${pageContext.request.contextPath}/board" method="post" style="display:flex; gap:10px;">
                <input type="hidden" name="action" value="publish">
                <input type="text" name="content" placeholder="说点什么吧..." style="flex:1; padding:10px; border:1px solid #eee; border-radius:4px; outline:none;" required>
                <button type="submit" style="background:var(--primary-color); color:#fff; border:none; padding:0 20px; border-radius:4px;">发布</button>
            </form>
        </div>

        <c:forEach items="${boardList}" var="msg">
            <div class="contact-card" style="margin-bottom:12px; display:block; padding:0;">
                
                <%-- ================== 上半部：内容展示与点击跳转 ================== --%>
                <a href="${pageContext.request.contextPath}/board?action=detail&id=${msg.id}" 
                   style="display:flex; text-decoration:none; color:inherit; padding:15px 15px 5px 15px;">
                    <img class="user-avatar avatar-contact-sm me-3" 
                         src="${pageContext.request.contextPath}/avatar/${empty msg.authorAvatar ? 'default.png' : msg.authorAvatar}" 
                         alt="用户头像" onerror="this.src='${pageContext.request.contextPath}/images/default.png'"/>
                         
                    <div class="contact-info" style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; color:#576b95;">${empty msg.authorName ? '匿名同学' : msg.authorName}</span>
                            <span style="font-size:12px; color:#999;"><fmt:formatDate value="${msg.createTime}" pattern="MM-dd HH:mm"/></span>
                        </div>
                        <div style="margin-top:6px; font-size:15px; color:#333; line-height:1.4;">${msg.content}</div>
                    </div>
                </a>
                
                <%-- ================== 下半部：独立的纯净交互大条 ================== --%>
                <div style="padding:10px 15px; display:flex; justify-content:flex-end; gap:25px; align-items:center;">
                    
                    <%-- 独立点赞表单 --%>
                    <form action="${pageContext.request.contextPath}/board" method="post" style="margin:0;">
                        <input type="hidden" name="action" value="like">
                        <input type="hidden" name="messageId" value="${msg.id}">
                        <button type="submit" style="background:none; border:none; color:#576b95; font-size:13px; font-weight:bold; cursor:pointer; padding:0; display:flex; align-items:center; gap:4px;">
                            <span style="font-size:16px;">👍</span> ${msg.likeCount}
                        </button>
                    </form>
                    
                    <%-- 独立回复跳转 --%>
                    <a href="${pageContext.request.contextPath}/board?action=detail&id=${msg.id}" 
                       style="color:#576b95; font-size:13px; font-weight:bold; text-decoration:none; display:flex; align-items:center; gap:4px;">
                        <span style="font-size:15px;">💬</span> ${msg.replies.size()}
                    </a>
                </div>

            </div>
        </c:forEach>
    </div>

<jsp:include page="/jsp/tabbar.jsp" />
</body>
</html>