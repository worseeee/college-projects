<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>留言详情与讨论</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
    <style>
        .reply-bar { position: fixed; bottom: 0; left: 0; width: 100%; padding: 10px; background: #f7f7f7; border-top: 1px solid #ddd; display: flex; z-index: 1000; box-sizing: border-box;}
    </style>
</head>
<body style="background:#f1f1f1; padding-bottom:70px;">

    <div class="header" style="position: sticky; top: 0; z-index: 100;">
        <a href="${pageContext.request.contextPath}/board" style="position:absolute; left:15px; text-decoration:none; color:#333;">&lt; 返回</a>
        留言详情
    </div>

    <%-- ⚠️ 详情页防刷提示 --%>
    <c:if test="${not empty sessionScope.flashMsg}">
        <div style="background-color: #fff3cd; color: #856404; padding: 10px; text-align: center; font-size: 13px; font-weight: bold;">
            ${sessionScope.flashMsg}
        </div>
        <c:remove var="flashMsg" scope="session"/>
    </c:if>

    <div style="padding:15px;">
        <%-- 主贴展示卡片 --%>
        <div class="contact-card" style="display:block; background:#fff; padding:20px; border-radius:8px; margin-bottom:15px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="font-size:16px; color:#111; line-height:1.6; border-top:1px solid #eee; padding-top:12px;">
                ${mainMsg.content}
            </div>
            
            <%-- ================== ✅ 新增：详情页大号居中点赞引擎 ================== --%>
            <div style="display:flex; justify-content:center; margin-top:25px; margin-bottom:5px;">
                <form action="${pageContext.request.contextPath}/board" method="post">
                    <input type="hidden" name="action" value="like">
                    <input type="hidden" name="messageId" value="${mainMsg.id}">
                    <input type="hidden" name="source" value="detail">
                    <button type="submit" style="background:#f1f1f1; border:1px solid #e0e0e0; border-radius:20px; padding:6px 28px; color:#576b95; font-size:14px; font-weight:bold; cursor:pointer; display:flex; align-items:center; gap:6px;">
                        <span style="font-size:18px;">👍</span> 赞 (${mainMsg.likeCount})
                    </button>
                </form>
            </div>
            <%-- ================================================================= --%>
            
        </div>

        <%-- 2. 评论与回复列表 --%>
        <div style="font-size:14px; color:#666; margin:10px 5px; font-weight:bold;">全部回复 (${replies.size()})</div>
        
        <c:choose>
            <c:when test="${empty replies}">
                <div style="text-align:center; padding:40px 0; color:#aaa; background:#fff; border-radius:8px;">
                    沙发空缺中，快来抢首发回复吧！🍵
                </div>
            </c:when>
            <c:otherwise>
                <div style="background:#fff; border-radius:8px; padding:10px 15px;">
                    <c:forEach items="${replies}" var="reply" varStatus="status">
                        <div style="display:flex; padding:12px 0; ${!status.last ? 'border-bottom:1px solid #f0f0f0;' : ''}">
                            <img class="user-avatar" style="width:36px; height:36px; border-radius:50%; margin-right:10px; flex-shrink:0;"
                                 src="${pageContext.request.contextPath}/avatar/${empty reply.authorAvatar ? 'default.png' : reply.authorAvatar}" 
                                 onerror="this.src='${pageContext.request.contextPath}/images/default.png'"/>
                            <div style="flex:1;">
                                <div style="display:flex; justify-content:space-between;">
                                    <span style="font-size:13px; font-weight:bold; color:#576b95;">${reply.authorName}</span>
                                    <span style="font-size:11px; color:#bbb;"><fmt:formatDate value="${reply.createTime}" pattern="MM-dd HH:mm"/></span>
                                </div>
                                <div style="font-size:14px; color:#333; margin-top:4px; line-height:1.4;">
                                    ${reply.content}
                                </div>
                            </div>
                        </div>
                    </c:forEach>
                </div>
            </c:otherwise>
        </c:choose>
    </div>

    <%-- 3. 底部固定回复输入框 (直接复用发布接口，通过 hidden 传递 parentId) --%>
    <form class="reply-bar" action="${pageContext.request.contextPath}/board" method="post">
        <input type="hidden" name="action" value="publish">
        <input type="hidden" name="parentId" value="${mainMsg.id}">
        <input type="text" name="content" required autocomplete="off" placeholder="回复 ${mainMsg.authorName}..." 
               style="flex:1; padding:8px 12px; border:1px solid #ddd; border-radius:18px; outline:none; font-size:14px; background:#fff;">
        <button type="submit" style="background:#07c160; color:#fff; border:none; padding:0 18px; border-radius:18px; margin-left:8px; font-weight:bold; font-size:14px;">回复</button>
    </form>

</body>
</html>