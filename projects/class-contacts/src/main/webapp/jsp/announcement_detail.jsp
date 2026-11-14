<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>回执详情交互中心</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/css/mobile.css">
</head>
<body style="background:#f5f5f9;">
    <div class="header">
        <a href="javascript:history.back()" style="position:absolute; left:15px; text-decoration:none; color:#333; font-weight:normal;">&lt; 返回</a>
        详情与收缴回执
    </div>

    <%-- ==================== ✅ 核心补齐：顶部成功反馈提示条 ==================== --%>
    <c:if test="${not empty sessionScope.flashMsg}">
        <div style="background-color: #d4edda; color: #155724; padding: 10px; text-align: center; font-size: 13px; font-weight: bold; border-bottom: 1px solid #c3e6cb;">
            ${sessionScope.flashMsg}
        </div>
        <c:remove var="flashMsg" scope="session"/>
    </c:if>
    <%-- ======================================================================= --%>

    <!-- 主公告展示区 -->
    <div style="padding:20px; background:#fff; margin-bottom:10px; border-bottom:1px solid #e5e5e5;">
        <span style="font-size:12px; padding:2px 6px; border-radius:3px; color:#fff; background:${announcement.category == '作业' ? '#f39c12' : '#07c160'}; vertical-align:middle;">${announcement.category}</span>
        <h2 style="margin-top:10px; font-size:20px; color:#333;">${announcement.title}</h2>
        <p style="font-size:15px; color:#444; margin:15px 0; line-height:1.6; white-space: pre-wrap;">${announcement.content}</p>
        
        <c:if test="${not empty announcement.attachmentUrl}">
            <div style="background:#e8f4fd; padding:12px; border-radius:6px; font-size:13px; border:1px solid #bae7ff; margin-top:15px;">
                📎 官方下发附件：<a href="${pageContext.request.contextPath}/${announcement.attachmentUrl}" target="_blank" style="color:#1890ff; text-decoration:underline; font-weight:bold; margin-left:5px;">查看/下载原始附件</a>
            </div>
        </c:if>
    </div>

    <!-- 学生角色：填报并上传作业附件 -->
    <div style="padding:15px; background:#fff; margin-bottom:10px; border-bottom:1px solid #e5e5e5;">
        <h4 style="color:#333; margin-bottom:15px; font-size:14px;">✍ 提交您的执行回执 / 作业回执</h4>
        
        <%-- ==================== ✅ 核心补齐：我的历史提交记录专属展示区 ==================== --%>
        <c:forEach items="${replies}" var="rep">
            <c:if test="${rep.userId == sessionScope.sessionUser.id}">
                <div style="background:#f8f9fa; border:1px solid #e2e3e5; padding:12px; border-radius:6px; margin-bottom:15px;">
                    <div style="font-size:13px; color:#28a745; font-weight:bold; margin-bottom:6px;">
                        ✅ 我已于 <fmt:formatDate value="${rep.submitTime}" pattern="MM-dd HH:mm"/> 成功提交：
                    </div>
                    <div style="font-size:14px; color:#444; background:#fff; padding:8px; border-radius:4px; border:1px solid #eee;">
                        ${rep.replyContent}
                    </div>
                    <c:if test="${not empty rep.fileUrl}">
                        <div style="margin-top:8px; font-size:13px;">
                            📎 我的附件: <a href="${pageContext.request.contextPath}/${rep.fileUrl}" target="_blank" style="color:#007bff; text-decoration:underline;">点击下载并验证文件</a>
                        </div>
                    </c:if>
                </div>
            </c:if>
        </c:forEach>
        <%-- ============================================================================== --%>

        <form action="${pageContext.request.contextPath}/announcementDetail" method="post" enctype="multipart/form-data">
            <input type="hidden" name="announcementId" value="${announcement.id}">
            <textarea name="replyContent" placeholder="在此输入给老师或班委的说明留言..." required style="width:100%; height:60px; border:1px solid #ddd; border-radius:4px; padding:8px; box-sizing:border-box; outline:none; font-size:14px;"></textarea>
            <div style="margin:10px 0; font-size:13px; color:#666;">
                上传我的附件文件: <input type="file" name="submitFile" style="margin-left:5px;">
            </div>
            <button type="submit" class="btn" style="padding:10px; background:#007bff; color:#fff; border:none; width:100%; border-radius:4px; font-weight:bold; font-size:14px; cursor:pointer;">确认提交回执数据</button>
        </form>
    </div>

    <!-- 教师/发布者权限专属区：集抄并收缴全班作业 -->
    <c:if test="${announcement.adminId == sessionScope.sessionUser.id}">
        <div style="padding:15px; background:#fff; margin-bottom:30px;">
            <h4 style="color:#e74c3c; margin-bottom:12px; font-size:14px; border-left:3px solid #e74c3c; padding-left:8px;">📊 全班收缴回执明细 (仅发布者可见)</h4>
            <c:if test="${empty replies}">
                <div style="text-align:center; color:#ccc; padding:20px 0; font-size:13px;">暂无学生提交任何回执</div>
            </c:if>
            <c:forEach items="${replies}" var="rep">
                <div style="border-bottom:1px solid #f0f0f0; padding:12px 0; font-size:14px;">
                    <div style="color:#576b95; font-weight:bold; display:flex; justify-content:between;">
                        <span>${rep.userName} <span style="font-weight:normal; color:#888; font-size:12px;">(${rep.studentNo})</span></span>
                    </div>
                    <div style="color:#333; margin:6px 0; background:#f9f9f9; padding:6px; border-radius:4px;">${rep.replyContent}</div>
                    <c:if test="${not empty rep.fileUrl}">
                        <div style="font-size:12px; margin-top:4px; color:#1890ff;">
                            📂 交付的文件: <a href="${pageContext.request.contextPath}/${rep.fileUrl}" target="_blank" style="color:#1890ff; text-decoration:underline; font-weight:bold;">下载该生提交的附件</a>
                        </div>
                    </c:if>
                    <div style="font-size:11px; color:#bbb; text-align:right; margin-top:4px;"><fmt:formatDate value="${rep.submitTime}" pattern="yyyy-MM-dd HH:mm"/></div>
                </div>
            </c:forEach>
        </div>
    </c:if>
</body>
</html>