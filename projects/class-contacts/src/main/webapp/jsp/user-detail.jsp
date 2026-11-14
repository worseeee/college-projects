<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学生详细档案 - ${targetUser.realName}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
    <style>
        /* 针对收藏胶囊按钮的微交互动画 */
        .btn-bookmark {
            border-radius: 50rem;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 10px rgba(243, 156, 18, 0.2);
        }
        .btn-bookmark:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(243, 156, 18, 0.3);
        }
    </style>
</head>
<body class="bg-light">

<div class="container py-4">
    <%-- 全局闪现消息操作反馈 (Toast / Alert) --%>
    <c:if test="${not empty flashMsg}">
        <div class="alert alert-${flashType} alert-dismissible fade show shadow-sm" role="alert">
            ${flashMsg}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    </c:if>

    <%-- 1. 头部个人档案卡片 --%>
    <div class="card shadow-sm mb-4 border-0">
        <div class="card-body text-center bg-white rounded p-4">
            <img src="${pageContext.request.contextPath}/avatar/${empty targetUser.avatar ? 'default.png' : targetUser.avatar}" 
                 class="avatar-profile-lg mb-3 rounded-circle shadow-sm" alt="头像"
                 style="width: 96px; height: 96px; object-fit: cover;">
            <h4 class="card-title font-weight-bold mb-1">${targetUser.realName}</h4>
            <p class="text-muted small mb-3">学号: ${targetUser.studentNo} | 身份: <span class="badge bg-secondary">${targetUser.classRole}</span></p>
            <hr class="text-black-50">
            <p class="card-text text-secondary px-3 fst-italic">"${empty targetUser.bio ? '这个人很懒，什么都没写~' : targetUser.bio}"</p>
            
            <%-- ==================== 新增：智能收藏/取消收藏闭环 ==================== --%>
            <%-- 只有在查看他人档案时 (relationStatus != -1)，才渲染收藏功能 --%>
            <c:if test="${relationStatus != -1}">
                <div class="mt-4 pt-2">
                    <c:choose>
                        <%-- 情况A：已经被我收藏 --%>
                        <c:when test="${isBookmarked}">
                            <a href="${pageContext.request.contextPath}/bookmark?action=remove&targetId=${targetUser.id}" 
                               class="btn btn-outline-warning btn-bookmark px-4 py-2 w-75 text-dark border-2">
                                🌟 已收藏 (点击取消)
                            </a>
                        </c:when>
                        <%-- 情况B：尚未收藏 --%>
                        <c:otherwise>
                            <a href="${pageContext.request.contextPath}/bookmark?action=add&targetId=${targetUser.id}" 
                               class="btn btn-warning btn-bookmark px-4 py-2 w-75 text-white" style="background-color: #f39c12; border-color: #f39c12;">
                                ⭐ 收藏该同学
                            </a>
                        </c:otherwise>
                    </c:choose>
                </div>
            </c:if>
            <%-- ================================================================= --%>
        </div>
    </div>

    <%-- 2. 核心社交关系操作按钮区 --%>
    <div class="d-grid gap-2 mb-4">
        <c:choose>
            <c:when test="${relationStatus == -1}">
                <a href="${pageContext.request.contextPath}/profile" class="btn btn-outline-primary btn-lg shadow-sm">⚙️ 修改我的个人资料</a>
            </c:when>
            <c:when test="${relationStatus == 1}">
                <a href="${pageContext.request.contextPath}/message?action=chat&targetId=${targetUser.id}" class="btn btn-success btn-lg shadow-sm">💬 发起私聊对话</a>
                <form action="${pageContext.request.contextPath}/friendship?action=delete" method="POST" onsubmit="return confirm('确定要解除好友关系吗？');" class="mt-1">
                    <input type="hidden" name="friendId" value="${targetUser.id}">
                    <button type="submit" class="btn btn-outline-danger w-100 btn-sm py-2">解除好友关系</button>
                </form>
            </c:when>
            <c:when test="${relationStatus == 2}">
                <button class="btn btn-secondary btn-lg shadow-sm" disabled>⏳ 好友申请审核中...</button>
            </c:when>
            <c:when test="${relationStatus == 3}">
                <div class="card p-3 border-warning bg-white shadow-sm">
                    <p class="small text-center text-dark font-weight-bold mb-2">👋 该同学向您发起了好友申请</p>
                    <div class="d-flex gap-2">
                        <a href="${pageContext.request.contextPath}/friendship?action=accept&requesterId=${targetUser.id}" class="btn btn-success flex-fill">同意</a>
                        <a href="${pageContext.request.contextPath}/friendship?action=reject&requesterId=${targetUser.id}" class="btn btn-outline-danger flex-fill">拒绝</a>
                    </div>
                </div>
            </c:when>
            <c:otherwise>
                <form action="${pageContext.request.contextPath}/friendship?action=add" method="POST">
                    <input type="hidden" name="friendId" value="${targetUser.id}">
                    <button type="submit" class="btn btn-primary btn-lg w-100 shadow-sm">➕ 申请添加为班级好友</button>
                </form>
            </c:otherwise>
        </c:choose>
    </div>

    <%-- 3. 联系方式受保护展示区 --%>
    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-white font-weight-bold py-3">
            <span class="text-primary">🛡️</span> 联系方式 <small class="text-muted fw-normal">（受班级隐私协议保护）</small>
        </div>
        <ul class="list-group list-group-flush">
            <li class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span class="text-muted">手机号码</span>
                <span class="font-monospace fw-bold text-dark">${targetUser.phone}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span class="text-muted">微信账号</span>
                <span class="text-dark">${targetUser.wechat}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span class="text-muted">QQ 号码</span>
                <span class="text-dark">${targetUser.qq}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span class="text-muted">居住宿舍</span>
                <span class="badge bg-info text-dark">${targetUser.dormitory}</span>
            </li>
        </ul>
    </div>
    
    <%-- 4. 底部返回导航 --%>
    <div class="text-center mt-3 mb-5">
        <%-- ❌ 原错误写法：href="${pageContext.request.contextPath}/contactList" --%>
        <%-- ✅ 核心修复：将路由路径改为真实匹配 ContactListServlet 的 /contacts --%>
        <a href="${pageContext.request.contextPath}/contacts" class="text-decoration-none text-secondary fw-bold">
            ← 返回班级通讯录
        </a>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>