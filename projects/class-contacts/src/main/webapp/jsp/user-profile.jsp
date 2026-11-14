<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>个人中心</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
    <style>
        .profile-header { background: #fff; padding: 30px 20px; text-align: center; margin-bottom: 10px; }
        .user-avatar { width: 80px; height: 80px; border-radius: 50%; box-shadow: 0 2px 10px rgba(0,0,0,0.1); object-fit:cover; border: 2px solid #fff; }
        .menu-list { background: #fff; }
        .menu-item { display: block; padding: 15px 20px; border-bottom: 1px solid #f0f0f0; color: #333; text-decoration: none; display: flex; justify-content: space-between; align-items: center; }
        /* 隐藏的修改表单面板 */
        .edit-panel { display: none; padding: 20px; background: #fafafa; border-bottom: 1px solid #eee; }
        
        /* 提示条样式 */
        .custom-alert {
            padding: 12px 15px; margin: 10px 15px; border-radius: 6px; font-size: 14px; font-weight: bold; text-align: center;
        }
        .alert-error { background: #fde8e8; color: #c81e1e; border: 1px solid #fbd5d5; }
        .alert-success { background: #def7ec; color: #03543f; border: 1px solid #bcf0da; }
    </style>
</head>
<body>
    <div class="header">我的个人中心</div>
    
    <%-- ==================== ✅ 核心补齐：全局错误与提示消息回显 ==================== --%>
    <c:if test="${not empty errorMsg}">
        <div class="custom-alert alert-error" id="msgAlert">❌ ${errorMsg}</div>
        <c:remove var="errorMsg" scope="request"/>
    </c:if>
    <c:if test="${not empty sessionScope.flashMsg}">
        <div class="custom-alert alert-success" id="msgAlert">🎉 ${sessionScope.flashMsg}</div>
        <c:remove var="flashMsg" scope="session"/>
    </c:if>
    <%-- =========================================================================== --%>
    
    <div class="profile-header">
		<img class="user-avatar" 
		     src="${pageContext.request.contextPath}/avatar/${empty sessionUser.avatar ? 'default.png' : sessionUser.avatar}" 
		     alt="用户头像" 
		     onerror="this.src='${pageContext.request.contextPath}/images/default.png'"/>
        <form action="${pageContext.request.contextPath}/avatarUpload" method="post" enctype="multipart/form-data" style="margin-top: 12px;">
            <label for="avatarInput" style="color: #07c160; font-size: 13px; cursor: pointer; border: 1px solid #07c160; padding: 4px 12px; border-radius: 15px; display: inline-block;">📸 更换头像</label>
            <input type="file" id="avatarInput" name="avatarFile" accept="image/*" style="display: none;" onchange="this.form.submit()">
        </form>
        <h2 style="margin-top: 15px; font-size: 20px; color: #333;">${sessionScope.sessionUser.realName}</h2>
        <p style="color: #999; font-size: 13px; margin-top: 5px;">学号: ${sessionScope.sessionUser.studentNo}</p>
    </div>

    <div class="menu-list">
        <%-- 折叠面板 1：基本资料与隐私 --%>
        <a href="javascript:void(0);" onclick="togglePanel('editPanel', 'arrowIcon1')" class="menu-item">
            <span>📝 基本资料与隐私设置</span> <span id="arrowIcon1">∨</span>
        </a>
        
        <div id="editPanel" class="edit-panel">
            <form action="${pageContext.request.contextPath}/profile" method="post">
                <input type="hidden" name="action" value="updateInfo">
                <div class="form-group"><input type="text" name="realName" value="${userInfo.realName}" placeholder="真实姓名" required></div>
                <div class="form-group"><input type="tel" name="phone" value="${userInfo.phone}" placeholder="手机号码"></div>
                <div class="form-group"><input type="text" name="wechat" value="${userInfo.wechat}" placeholder="微信号"></div>
                <div class="form-group"><input type="text" name="qq" value="${userInfo.qq}" placeholder="QQ号"></div>
                <div class="form-group"><input type="text" name="dormitory" value="${userInfo.dormitory}" placeholder="宿舍(如:12-404)"></div>
                <div class="form-group"><input type="text" name="classRole" value="${userInfo.classRole}" placeholder="班委身份 (如: 学生, 班长, 体育委员)"></div>
                <div class="form-group"><input type="text" name="bio" value="${userInfo.bio}" placeholder="个人简介 (一句话介绍自己)"></div>
                <button type="submit" class="btn" style="padding:10px; font-size:14px; width:100%;">保存基本资料</button>
            </form>
            
            <hr style="border:0; border-top:1px dashed #ccc; margin:20px 0;">
            
            <form action="${pageContext.request.contextPath}/profile" method="post">
                <input type="hidden" name="action" value="updatePrivacy">
                <div style="font-size:13px; color:#666; margin-bottom:10px; font-weight:bold;">🛡️ 隐私权限控制 (0:公开, 1:仅好友, 2:私密)</div>
                <div class="form-group" style="display:flex; justify-content:space-between; align-items:center;">
                    <label style="font-size:14px; color:#555;">手机号权限:</label>
                    <input type="number" name="privacyPhone" value="${userInfo.privacyPhone}" min="0" max="2" style="width:70px; padding:6px; text-align:center; border:1px solid #ddd; border-radius:4px;">
                </div>
                <div class="form-group" style="display:flex; justify-content:space-between; align-items:center;">
                    <label style="font-size:14px; color:#555;">微信号权限:</label>
                    <input type="number" name="privacyWechat" value="${userInfo.privacyWechat}" min="0" max="2" style="width:70px; padding:6px; text-align:center; border:1px solid #ddd; border-radius:4px;">
                </div>
                <div class="form-group" style="display:flex; justify-content:space-between; align-items:center;">
                    <label style="font-size:14px; color:#555;">QQ号权限:</label>
                    <input type="number" name="privacyQq" value="${userInfo.privacyQq}" min="0" max="2" style="width:70px; padding:6px; text-align:center; border:1px solid #ddd; border-radius:4px;">
                </div>
                <button type="submit" class="btn" style="padding:10px; font-size:14px; background:#f39c12; width:100%;">更新隐私设置</button>
            </form>
        </div>
        
        <%-- ==================== ✅ 核心补齐：折叠面板 2：修改密码 ==================== --%>
        <a href="javascript:void(0);" onclick="togglePanel('pwdPanel', 'arrowIcon2')" class="menu-item">
            <span>🔒 修改登录密码</span> <span id="arrowIcon2">∨</span>
        </a>
        
        <div id="pwdPanel" class="edit-panel">
            <form action="${pageContext.request.contextPath}/profile" method="post" onsubmit="return validatePwdForm(this)">
                <input type="hidden" name="action" value="changePwd">
                <div style="font-size:13px; color:#666; margin-bottom:12px;">定期更换密码可以更好地保护您的个人账号安全。</div>
                <div class="form-group">
                    <input type="password" name="oldPassword" placeholder="请输入原登录密码" required 
                           style="width:100%; padding:10px; border:1px solid #ddd; border-radius:6px; box-sizing:border-box;">
                </div>
                <div class="form-group" style="margin-top:10px;">
                    <input type="password" name="newPassword" id="newPwd" placeholder="请输入新登录密码 (不少于6位)" required minlength="6"
                           style="width:100%; padding:10px; border:1px solid #ddd; border-radius:6px; box-sizing:border-box;">
                </div>
                <div class="form-group" style="margin-top:10px;">
                    <input type="password" id="confirmPwd" placeholder="请再次确认新密码" required minlength="6"
                           style="width:100%; padding:10px; border:1px solid #ddd; border-radius:6px; box-sizing:border-box;">
                </div>
                <button type="submit" class="btn" style="padding:10px; font-size:14px; background:#007bff; width:100%; margin-top:10px;">提交确认修改</button>
            </form>
        </div>
        <%-- ========================================================================= --%>
		<%-- ==================== ✅ 核心补齐：个人中心-好友大厅专属通道 ==================== --%>
        <a href="${pageContext.request.contextPath}/friendship?action=list" class="menu-item" style="border-top: 8px solid #f5f5f5;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 18px; margin-right: 10px;">👥</span>
                <span style="font-size: 15px; color: #333; font-weight: 500;">我的好友与申请大厅</span>
            </div>
            <span style="color: #bbb; font-weight: bold;">&gt;</span>
        </a>
        <c:if test="${sessionScope.sessionUser.role == 2}">
            <a href="${pageContext.request.contextPath}/admin/audit" class="menu-item" style="color: #07c160; font-weight: bold;">
                <span>⚙️ 进入后台管理 (新生审核)</span> <span>></span>
            </a>
        </c:if>
    </div>
    
    <div style="padding: 25px 20px;">
        <a href="${pageContext.request.contextPath}/logout" class="btn" style="background-color: #e74c3c; display: block; text-align: center; text-decoration: none; padding: 12px 0; border-radius: 8px;">退出当前登录</a>
    </div>

    <jsp:include page="/jsp/tabbar.jsp" />

    <script>
        // 通用面板切换交互
        function togglePanel(panelId, iconId) {
            var panel = document.getElementById(panelId);
            var icon = document.getElementById(iconId);
            if (panel.style.display === "block") {
                panel.style.display = "none";
                icon.innerText = "∨";
            } else {
                panel.style.display = "block";
                icon.innerText = "∧";
            }
        }

        // 前端密码一致性校验
        function validatePwdForm(form) {
            var newPwd = document.getElementById("newPwd").value;
            var confirmPwd = document.getElementById("confirmPwd").value;
            if (newPwd !== confirmPwd) {
                alert("⚠️ 两次输入的新密码不一致，请重新检查！");
                return false;
            }
            if (newPwd === form.oldPassword.value) {
                alert("⚠️ 新密码不能与原密码相同！");
                return false;
            }
            return true;
        }

        // 3秒后自动隐藏提示条
        setTimeout(function() {
            var alertBox = document.getElementById("msgAlert");
            if(alertBox) {
                alertBox.style.opacity = '0';
                alertBox.style.transition = 'opacity 0.5s';
                setTimeout(function() { alertBox.style.display = 'none'; }, 500);
            }
        }, 3500);
    </script>
</body>
</html>