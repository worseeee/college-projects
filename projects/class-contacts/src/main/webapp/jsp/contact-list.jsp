<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>通讯录大厅</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
    <style>
        /* 兼容补充：确保微型头像类在移动端不变形 */
        .avatar-contact-sm {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            object-fit: cover;
            flex-shrink: 0;
        }
        .me-3 {
            margin-right: 12px;
        }
    </style>
</head>
<body>

    <div class="header">2023级物联网工程1班</div>

    <div style="padding: 10px; background: #fff;">
        <input type="text" placeholder="🔍 搜索姓名、宿舍或标签" 
               style="width: 100%; padding: 8px 15px; border-radius: 20px; border: 1px solid #eee; background: #f7f7f7; outline: none;">
    </div>

    <%-- ==================== ✅ 核心补齐：好友大厅常驻点击入口 ==================== --%>
    <div style="padding: 8px 15px 12px 15px; background: #fff; border-bottom: 8px solid #f1f1f1;">
        <a href="${pageContext.request.contextPath}/friendship?action=list" 
           style="display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 14px 18px; border-radius: 12px; text-decoration: none; color: #2e7d32; box-shadow: 0 2px 6px rgba(0,0,0,0.04); transition: transform 0.1s;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 26px; margin-right: 14px;">👥</span>
                <div>
                    <div style="font-size: 16px; font-weight: bold; color: #1b5e20;">我的好友与申请大厅</div>
                    <div style="font-size: 12px; color: #388e3c; margin-top: 3px;">查看已结缘伙伴 · 审批新的好友申请</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 13px; font-weight: bold; color: #2e7d32; background: rgba(255,255,255,0.6); padding: 4px 10px; border-radius: 15px;">点击进入</span>
                <span style="font-size: 18px; color: #1b5e20; font-weight: bold;">&gt;</span>
            </div>
        </a>
    </div>
    <%-- ========================================================================= --%>

    <div class="contact-list">
        <c:forEach items="${contactList}" var="contact">
		    <div class="contact-card">
		        
		        <%-- ✅ 核心修复：添加超链接包裹，点击头像或姓名即可一键进入《用户档案与社交互动大厅》 --%>
		        <a href="${pageContext.request.contextPath}/userDetail?id=${contact.id}" 
		           style="display: flex; align-items: center; text-decoration: none; color: inherit; flex: 1; overflow: hidden;">
		            
		            <img class="user-avatar avatar-contact-sm me-3" 
		                 src="${pageContext.request.contextPath}/avatar/${empty contact.avatar ? 'default.png' : contact.avatar}" 
		                 alt="用户头像" 
		                 onerror="this.src='${pageContext.request.contextPath}/images/default.png'"/>
		            
		            <div class="contact-info">
		                <div class="contact-name">${contact.realName} 
		                    <span style="font-size: 12px; color: #999;">(${contact.dormitory})</span>
		                </div>
		                <div class="contact-tags">
		                    <span style="background: #e1f5fe; color: #0288d1; padding: 2px 6px; border-radius: 4px; font-size: 11px;">
		                        ${contact.classRole}
		                    </span>
		                    <span style="background: none; color: #666; margin-left: 5px;">📞 ${contact.phone}</span>
		                </div>
		            </div>
		        </a>
		        
		        <%-- 右侧拨号按钮保持不变 --%>
		        <div class="contact-action">
		            <c:choose>
		                <c:when test="${contact.phone.contains('*')}">
		                    <span style="font-size: 12px; color: #ccc;">不可拨打</span>
		                </c:when>
		                <c:otherwise>
		                    <a href="tel:${contact.phone}" style="padding: 6px 12px; background: #4caf50; color: white; border-radius: 15px; text-decoration: none; font-size: 13px;">拨打</a>
		                </c:otherwise>
		            </c:choose>
		        </div>
		    </div>
		</c:forEach>
    </div>
	
	</div> <%-- ==================== ✅ 新增：通讯录底部分页导航条 ==================== --%>
    <%-- 只有当总页数大于 1 页（即人数超过 15 人）时，才自动浮现分页控件 --%>
    <c:if test="${totalPages > 1}">
        <div style="display: flex; justify-content: center; align-items: center; padding: 15px 10px 80px 10px; background: #f1f1f1; gap: 15px;">
            
            <%-- 上一页按钮 (如果是第 1 页，则变灰不可点击) --%>
            <c:choose>
                <c:when test="${currentPage <= 1}">
                    <span style="padding: 6px 14px; background: #e0e0e0; color: #999; border-radius: 15px; font-size: 13px; user-select: none;">上一页</span>
                </c:when>
                <c:otherwise>
                    <a href="${pageContext.request.contextPath}/contacts?page=${currentPage - 1}&keyword=${keyword}" 
                       style="padding: 6px 14px; background: #07c160; color: white; border-radius: 15px; font-size: 13px; text-decoration: none; box-shadow: 0 2px 5px rgba(7,193,96,0.2);">上一页</a>
                </c:otherwise>
            </c:choose>
            
            <%-- 中间页码指示器 --%>
            <span style="font-size: 14px; font-weight: bold; color: #555;">
                第 <span style="color: #07c160;">${currentPage}</span> / ${totalPages} 页
            </span>
            
            <%-- 下一页按钮 (如果是最后 1 页，则变灰不可点击) --%>
            <c:choose>
                <c:when test="${currentPage >= totalPages}">
                    <span style="padding: 6px 14px; background: #e0e0e0; color: #999; border-radius: 15px; font-size: 13px; user-select: none;">下一页</span>
                </c:when>
                <c:otherwise>
                    <a href="${pageContext.request.contextPath}/contacts?page=${currentPage + 1}&keyword=${keyword}" 
                       style="padding: 6px 14px; background: #07c160; color: white; border-radius: 15px; font-size: 13px; text-decoration: none; box-shadow: 0 2px 5px rgba(7,193,96,0.2);">下一页</a>
                </c:otherwise>
            </c:choose>
            
        </div>
    </c:if>
    <%-- ===================================================================== --%>

    <jsp:include page="/jsp/tabbar.jsp" />
    
    <script>
        // 1. 实现前端实时搜索 (过滤 DOM 元素，实现无刷新体验)
        document.addEventListener("DOMContentLoaded", function() {
            const searchInput = document.querySelector('input[type="text"]');
            const contactCards = document.querySelectorAll('.contact-card');
    
            searchInput.addEventListener('input', function(e) {
                const keyword = e.target.value.toLowerCase().trim();
                
                contactCards.forEach(card => {
                    // 提取卡片内的文本内容（包含姓名、宿舍号、标签、手机号等）
                    const cardText = card.innerText.toLowerCase();
                    if (cardText.includes(keyword)) {
                        card.style.display = 'flex'; // 显示匹配项
                    } else {
                        card.style.display = 'none'; // 隐藏不匹配项
                    }
                });
            });
        });
    
        // 2. 实现点击微信号/QQ号自动复制功能 (模拟微信原生体验)
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('copyable')) {
                const textToCopy = e.target.getAttribute('data-clipboard-text');
                
                if (navigator.clipboard && window.isSecureContext) {
                    // navigator.clipboard 必须在 HTTPS 或 localhost 环境下才可用
                    navigator.clipboard.writeText(textToCopy).then(() => {
                        showToast('已复制到剪贴板');
                    }).catch(err => {
                        console.error('复制失败', err);
                    });
                } else {
                    // 兼容老版本浏览器的降级方案
                    let textArea = document.createElement("textarea");
                    textArea.value = textToCopy;
                    textArea.style.position = "fixed";
                    textArea.style.left = "-999999px";
                    textArea.style.top = "-999999px";
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    try {
                        document.execCommand('copy');
                        showToast('已复制: ' + textToCopy);
                    } catch (err) {
                        console.error('复制失败', err);
                    }
                    textArea.remove();
                }
            }
        });
    
        // 3. 移动端轻量级 Toast 提示框
        function showToast(message) {
            const toast = document.createElement('div');
            toast.textContent = message;
            toast.style.cssText = `
                position: fixed;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 14px;
                z-index: 9999;
                transition: opacity 0.3s;
            `;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 2000);
        }
    </script>

</body>
</html>