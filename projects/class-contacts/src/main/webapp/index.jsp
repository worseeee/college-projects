<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%
    // 首页路由网关：不展示任何内容，仅负责分发
    
    // 1. 尝试从 Session 中获取登录凭证
    Object sessionUser = session.getAttribute("sessionUser");
    
    if (sessionUser != null) {
        // 2. 如果已登录，重定向到通讯录大厅的 Servlet 接口
        response.sendRedirect(request.getContextPath() + "/contacts");
    } else {
        // 3. 如果未登录，重定向到登录页的 Servlet 接口
        response.sendRedirect(request.getContextPath() + "/login");
    }
%>