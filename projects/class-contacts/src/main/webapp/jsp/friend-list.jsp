<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>我的好友</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body>
    <div class="header">通讯录好友</div>
    
    <c:if test="${not empty flashMsg}">
	    <div class="alert alert-${not empty flashType ? flashType : 'info'}" 
	         style="padding: 12px; margin: 15px; border-radius: 4px; text-align: center; font-weight: bold;
	                background-color: ${flashType == 'success' ? '#d4edda' : (flashType == 'warning' ? '#fff3cd' : (flashType == 'danger' ? '#f8d7da' : '#d1ecf1'))};
	                color: ${flashType == 'success' ? '#155724' : (flashType == 'warning' ? '#856404' : (flashType == 'danger' ? '#721c24' : '#0c5460'))};">
	        ${flashMsg}
	    </div>
	</c:if>
	
    <div class="contact-list" style="padding-bottom:80px;">
        <c:if test="${not empty pendingRequests}">
            <h4 style="margin:10px 0; color:#e67e22; padding:0 10px;">新的好友申请</h4>
            <c:forEach items="${pendingRequests}" var="req">
                <div class="contact-card">
                    <div class="contact-info">
                        <div class="contact-name" style="font-weight:bold;">${req.friendName}</div>
                        <div style="font-size:12px; color:#999; margin-top:2px;">请求添加你为好友</div>
                    </div>
                    <div>
                        <!-- 【核心修复】将 requesterId 绑定修改为真正的申请人 id：req.userId -->
                        <a href="${pageContext.request.contextPath}/friendship?action=accept&requesterId=${req.userId}" style="color:#07c160; text-decoration:none; margin-right:15px; font-weight:bold; font-size:14px;">同意</a>
                        <a href="${pageContext.request.contextPath}/friendship?action=reject&requesterId=${req.userId}" style="color:#e74c3c; text-decoration:none; font-size:14px;">拒绝</a>
                    </div>
                </div>
            </c:forEach>
        </c:if>

        <h4 style="margin:20px 0 10px 0; color:#333; padding:0 10px;">我的好友 (${friends.size()})</h4>
        <c:if test="${empty friends}">
            <div style="text-align:center; color:#ccc; margin-top:4px; font-size:13px;">暂无通过的好友</div>
        </c:if>
        <c:forEach items="${friends}" var="f">
            <div class="contact-card">
                <div class="contact-info">
                    <div class="contact-name" style="font-weight:bold;">${f.friendName}</div>
                    <div style="font-size:12px; color:#999; margin-top:2px;">${f.friendBio == null ? '同学关系' : f.friendBio}</div>
                </div>
                <div>
                    <a href="${pageContext.request.contextPath}/message?action=chat&targetId=${f.friendId}" style="padding:6px 14px; border:1px solid #07c160; color:#07c160; border-radius:15px; text-decoration:none; font-size:12px; font-weight:bold; background:#fff;">发私信</a>
                </div>
            </div>
        </c:forEach>
    </div>
    <jsp:include page="/jsp/tabbar.jsp" />
</body>
</html>