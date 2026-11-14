package com.contacts.controller;

import com.contacts.entity.User;
import com.contacts.service.UserService;

import java.io.IOException;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/admin/audit")
public class AdminAuditServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private UserService userService = new UserService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        
        // 获取待审核列表
        List<User> pendingUsers = userService.getPendingUsers(sessionUser.getRole());
        request.setAttribute("pendingUsers", pendingUsers);
        
        // 【核心注意】必须转发到你的物理 JSP 文件名 admin_audit.jsp
        request.getRequestDispatcher("/jsp/admin_audit.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        String ipAddress = request.getRemoteAddr();

        int targetUserId = Integer.parseInt(request.getParameter("userId"));
        int actionStatus = Integer.parseInt(request.getParameter("actionStatus")); // 1通过 2拒绝
        
        userService.auditUser(targetUserId, actionStatus, sessionUser.getId(), sessionUser.getRole(), ipAddress);
        
        // 重定向回审核列表
        response.sendRedirect(request.getContextPath() + "/admin/audit");
    }
}