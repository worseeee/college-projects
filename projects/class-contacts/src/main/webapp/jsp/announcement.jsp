<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>班级公告/作业区</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body>
    <div class="header">公告与作业大厅</div>
    <div class="contact-list" style="padding-bottom:80px;">
        
        <c:if test="${sessionScope.sessionUser.role == 2 || sessionScope.sessionUser.canPublishAnnouncement == 1}">
            <div class="contact-card" style="display:block; padding:15px; margin-bottom:15px; background:#fff;">
                <form action="${pageContext.request.contextPath}/announcement" method="post" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="add">
                    <input type="text" name="title" placeholder="公告/作业标题" required style="width:100%; padding:8px; border:1px solid #eee; border-radius:4px; margin-bottom:8px; box-sizing:border-box; outline:none;">
                    <textarea name="content" placeholder="具体正文要求..." required style="width:100%; height:60px; border:1px solid #eee; border-radius:4px; padding:8px; box-sizing:border-box; outline:none;"></textarea>
                    
                    <div style="margin:6px 0; font-size:12px; color:#666;">
                        上传原始附件: <input type="file" name="attachment">
                    </div>
                    
                    <div style="display:flex; gap:8px; margin-top:8px;">
                        <select name="category" style="padding:6px; border:1px solid #eee; border-radius:4px;">
                            <option value="通知">📢 发布通知</option>
                            <option value="作业">📝 布置作业</option>
                        </select>
                        <select name="isTop" style="padding:6px; border:1px solid #eee; border-radius:4px;"><option value="0">普通</option><option value="1">置顶</option></select>
                        <input type="datetime-local" name="expireTime" style="flex:1; padding:6px; border:1px solid #eee; border-radius:4px;">
                    </div>
                    <button type="submit" class="btn" style="padding:10px; margin-top:10px; background:var(--primary-color); color:#fff; font-weight:bold; border:none; width:100%; border-radius:4px;">发布给全班</button>
                </form>
            </div>
        </c:if>

        <c:forEach items="${announcements}" var="a">
            <div class="contact-card" style="display:block; padding:15px; margin-bottom:12px; background:#fff; border-left: 4px solid ${a.category == '作业' ? '#f39c12' : '#07c160'};">
                <h3 style="color:#333; margin:0 0 6px 0; font-size:16px;">
                    <span style="font-size:11px; padding:2px 5px; border-radius:3px; margin-right:5px; color:#fff; background:${a.category == '作业' ? '#f39c12' : '#07c160'};">${a.category}</span>
                    <c:if test="${a.isTop == 1}"><span style="color:red; font-size:12px;">[置顶]</span></c:if>
                    ${a.title}
                </h3>
                <p style="font-size:14px; color:#555; line-height:1.5; margin:0 0 10px 0;">${a.content}</p>
                
                <div style="background:#f9f9f9; padding:8px; border-radius:4px; font-size:12px; color:#777; margin-bottom:10px;">
                    <div>👤 发布人: <strong>${a.adminName}</strong></div>
                    <div style="margin-top:2px;">🕒 发布时间: <fmt:formatDate value="${a.createTime}" pattern="yyyy-MM-dd HH:mm"/></div>
                    <c:if test="${not empty a.expireTime}">
                        <div style="margin-top:2px; color:#e74c3c;">⏳ 截止时间: <fmt:formatDate value="${a.expireTime}" pattern="yyyy-MM-dd HH:mm"/></div>
                    </c:if>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; font-size:13px;">
                    <c:choose>
                        <c:when test="${a.category == '通知'}">
                            <span style="color:#07c160; font-weight:bold;">已读 ${a.readCount} | 未读 ${a.unreadCount}</span>
                        </c:when>
                        <c:otherwise>
                            <span style="color:#e67e22; font-weight:bold;">已交 ${a.submittedCount} | 未交 ${a.unsubmittedCount}</span>
                        </c:otherwise>
                    </c:choose>
                    <a href="${pageContext.request.contextPath}/announcementDetail?id=${a.id}" style="padding:4px 12px; background:#007bff; color:#fff; text-decoration:none; border-radius:15px; font-size:12px;">查看详情/回复</a>
                </div>
            </div>
        </c:forEach>
    </div>
    <jsp:include page="/jsp/tabbar.jsp" />
</body>
</html>