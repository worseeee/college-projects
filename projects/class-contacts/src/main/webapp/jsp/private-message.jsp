<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>与 ${targetUser.realName} 私聊中</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
    <style>
        /* ==================== 纯正微信 App 私聊 UI 核心排版引擎 ==================== */
        body {
            background-color: #ededed !important; /* 微信官方聊天背景灰 */
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
        }

        /* 顶部导航栏 (灰底与分隔线控制) */
        .wx-header {
            background-color: #ededed;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
            font-weight: 600;
            color: #181818;
            border-bottom: 1px solid #dcdcdc;
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 0 15px;
        }
        .wx-header .back-btn {
            position: absolute;
            left: 15px;
            text-decoration: none;
            color: #181818;
            font-size: 16px;
            display: flex;
            align-items: center;
        }

        /* 聊天主窗体：提供充足的行间距与底部输入栏留白 */
        .chat-container {
            padding: 20px 15px 85px 15px;
            box-sizing: border-box;
            min-height: calc(100vh - 50px);
        }

        /* 单行消息外层 flex 容器：绝对保证每条对话有 22px 的上下安全间距 */
        .msg-row {
            display: flex;
            align-items: flex-start;
            margin-bottom: 22px;
            width: 100%;
        }
        .msg-row.other {
            flex-direction: row;
            justify-content: flex-start;
        }
        .msg-row.me {
            flex-direction: row-reverse;
            justify-content: flex-start;
        }

        /* 微信经典正方形微圆角头像 (严格锁死 42x42px，杜绝变形) */
        .msg-avatar {
            width: 42px !important;
            height: 42px !important;
            border-radius: 6px !important;
            object-fit: cover !important;
            flex-shrink: 0 !important;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        .msg-row.other .msg-avatar {
            margin-right: 12px;
        }
        .msg-row.me .msg-avatar {
            margin-left: 12px;
        }

        /* 消息内容横向包装器：核心突破！让气泡与“已读/未读”横向紧贴排列 */
        .msg-content-wrap {
            display: flex;
            align-items: flex-end;
            max-width: 72%;
        }
        .msg-row.other .msg-content-wrap {
            flex-direction: row;
        }
        .msg-row.me .msg-content-wrap {
            flex-direction: row-reverse;
        }

        /* 聊天气泡本体与微型小尖角 (Triangular Pointer) */
        .msg-bubble {
            padding: 11px 14px;
            border-radius: 6px;
            font-size: 16px;
            line-height: 1.5;
            word-break: break-all;
            position: relative;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        /* 左侧对端同学：纯白气泡 + 左侧指向尖角 */
        .msg-row.other .msg-bubble {
            background-color: #ffffff;
            color: #191919;
            border-top-left-radius: 2px;
        }
        .msg-row.other .msg-bubble::before {
            content: "";
            position: absolute;
            top: 14px;
            left: -6px;
            width: 0;
            height: 0;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
            border-right: 6px solid #ffffff;
        }

        /* 右侧本人：微信官方标准绿 (#95ec69) + 右侧指向尖角 */
        .msg-row.me .msg-bubble {
            background-color: #95ec69;
            color: #111111;
            border-top-right-radius: 2px;
        }
        .msg-row.me .msg-bubble::before {
            content: "";
            position: absolute;
            top: 14px;
            right: -6px;
            width: 0;
            height: 0;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
            border-left: 6px solid #95ec69;
        }

        /* 已读 / 未读状态标签：精巧锚定在绿气泡左侧底缘 */
        .status-tag {
            font-size: 11px;
            margin: 0 8px;
            margin-bottom: 2px;
            white-space: nowrap;
            flex-shrink: 0;
        }
        .status-tag.unread {
            color: #fa5151; /* 微信原生警告红 */
            font-weight: 600;
        }
        .status-tag.read {
            color: #b2b2b2;
        }

        /* 底部消息发送栏 (App 风格吸底与防软键盘遮挡) */
        .chat-input-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            min-height: 58px;
            padding: 8px 12px;
            background-color: #f7f7f7;
            border-top: 1px solid #dcdcdc;
            display: flex;
            align-items: center;
            box-sizing: border-box;
            z-index: 1000;
        }
        .chat-input-bar input[type="text"] {
            flex: 1;
            padding: 10px 14px;
            border: none;
            border-radius: 6px;
            background-color: #ffffff;
            font-size: 16px;
            outline: none;
            box-shadow: 0 1px 1px rgba(0,0,0,0.02);
        }
        .chat-input-bar button {
            background-color: #07c160;
            color: #ffffff;
            border: none;
            padding: 0 20px;
            height: 40px;
            border-radius: 6px;
            margin-left: 10px;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            flex-shrink: 0;
        }
        .chat-input-bar button:active {
            background-color: #06ad56;
        }

        /* 顶部安全提示条 */
        .custom-alert {
            margin: 10px 15px 0 15px;
            padding: 12px 35px 12px 15px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            position: relative;
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .custom-alert .close-btn {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            font-size: 18px;
            color: #856404;
            opacity: 0.6;
            cursor: pointer;
            padding: 0 5px;
        }
    </style>
</head>
<body>
    <div class="wx-header">
        <a href="javascript:history.back()" class="back-btn">&lt; 返回</a>
        <span>${targetUser.realName}</span>
    </div>

    <c:if test="${not empty sessionScope.chatError}">
        <div class="custom-alert" id="errorAlert">
            ${sessionScope.chatError}
            <button type="button" class="close-btn" onclick="document.getElementById('errorAlert').style.display='none'">&times;</button>
        </div>
        <c:remove var="chatError" scope="session"/>
    </c:if>

    <div class="chat-container" id="chatBox">
        <c:if test="${empty chatHistory}">
            <div style="text-align:center; color:#b2b2b2; margin-top:60px; font-size:14px;">
                — 你们俩还没有聊过天，打个招呼吧 —
            </div>
        </c:if>

        <c:forEach items="${chatHistory}" var="msg">
            <div class="msg-row ${msg.senderId == sessionScope.sessionUser.id ? 'me' : 'other'}">
                
                <%-- 1. 渲染左右对齐的正方形圆角头像 --%>
                <c:choose>
                    <c:when test="${msg.senderId == sessionScope.sessionUser.id}">
                        <%-- 右侧：本人头像 --%>
                        <img class="msg-avatar" 
                             src="${pageContext.request.contextPath}/avatar/${empty sessionScope.sessionUser.avatar ? 'default.png' : sessionScope.sessionUser.avatar}" 
                             alt="我" 
                             onerror="this.src='${pageContext.request.contextPath}/images/default.png'"/>
                    </c:when>
                    <c:otherwise>
                        <%-- 左侧：对方同学头像 --%>
                        <img class="msg-avatar" 
                             src="${pageContext.request.contextPath}/avatar/${empty targetUser.avatar ? 'default.png' : targetUser.avatar}" 
                             alt="${targetUser.realName}" 
                             onerror="this.src='${pageContext.request.contextPath}/images/default.png'"/>
                    </c:otherwise>
                </c:choose>

                <%-- 2. 消息内容横向包装器 (解决文字挤压的核心) --%>
                <div class="msg-content-wrap">
                    <%-- 聊天气泡本体 --%>
                    <div class="msg-bubble">${msg.content}</div>
                    
                    <%-- 已读 / 未读小红标 (仅在自己发出的绿色气泡左下角贴靠) --%>
                    <c:if test="${msg.senderId == sessionScope.sessionUser.id}">
                        <span class="status-tag ${msg.isRead == 1 ? 'read' : 'unread'}">
                            ${msg.isRead == 1 ? '已读' : '未读'}
                        </span>
                    </c:if>
                </div>

            </div>
        </c:forEach>
    </div>

    <form class="chat-input-bar" action="${pageContext.request.contextPath}/message?action=send" method="post">
        <input type="hidden" name="targetId" value="${targetUser.id}">
        <input type="text" name="content" required autocomplete="off" placeholder="发送消息...">
        <button type="submit">发送</button>
    </form>
    
    <script>
        window.onload = function() {
            // 页面加载完毕后，平滑滚动到最底部的最新一条消息
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        };
    </script>
</body>
</html>