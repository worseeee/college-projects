<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ page import="com.contacts.entity.User" %>
<%@ page import="com.contacts.dao.PrivateMessageDao" %>
<% 
    String uri = request.getRequestURI();
    // 【核心新增功能】实时探查当前登录同学的未读私信总数
    User loginUser = (User) session.getAttribute("sessionUser");
    int unreadMsgCount = 0;
    if(loginUser != null) {
        PrivateMessageDao _pmDao = new PrivateMessageDao();
        unreadMsgCount = _pmDao.getUnreadCount(loginUser.getId());
    }
%>
<style>
    /* 微信 App 风格红点气泡样式 */
    .icon-wrapper {
        position: relative;
        display: inline-block;
    }
    .badge-red-dot {
        position: absolute;
        top: -5px;
        right: -10px;
        background-color: #fa5151; /* 微信官方提示红 */
        color: #ffffff;
        font-size: 11px;
        font-weight: bold;
        height: 18px;
        min-width: 18px;
        line-height: 18px;
        border-radius: 9px;
        padding: 0 5px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        border: 1px solid #ffffff;
    }
</style>
<div class="tab-bar">
    <a href="${pageContext.request.contextPath}/contacts" class="tab-item <%= uri.contains("/contacts") || uri.contains("/userDetail") ? "active" : "" %>">
        <div style="font-size: 20px;">👥</div><div>通讯录</div>
    </a>
    <a href="${pageContext.request.contextPath}/message?action=list" class="tab-item <%= uri.contains("/message") && !uri.contains("action=chat") ? "active" : "" %>">
        <div class="icon-wrapper">
            <div style="font-size: 20px;">💬</div>
            <%-- 只有当未读数大于0时才展示红点，大于99则展示 99+ --%>
            <% if(unreadMsgCount > 0) { %>
                <span class="badge-red-dot"><%= unreadMsgCount > 99 ? "99+" : unreadMsgCount %></span>
            <% } %>
        </div>
        <div>消息</div>
    </a>
    <a href="${pageContext.request.contextPath}/announcement" class="tab-item <%= uri.contains("/announcement") ? "active" : "" %>">
        <div style="font-size: 20px;">📢</div><div>公告作业</div>
    </a>
    <a href="${pageContext.request.contextPath}/board" class="tab-item <%= uri.contains("/board") ? "active" : "" %>">
        <div style="font-size: 20px;">📝</div><div>留言板</div>
    </a>
    <a href="${pageContext.request.contextPath}/profile" class="tab-item <%= uri.contains("/profile") ? "active" : "" %>">
        <div style="font-size: 20px;">👤</div><div>我的</div>
    </a>
</div>