package com.contacts.controller;

import com.contacts.entity.User;
import com.contacts.service.UserService;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/profile")
public class UserProfileServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private UserService userService = new UserService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        User currentUserInfo = userService.getUserById(sessionUser.getId());
        request.setAttribute("userInfo", currentUserInfo);
        request.getRequestDispatcher("/jsp/user-profile.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        String action = request.getParameter("action");
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        String ipAddress = request.getRemoteAddr();

        if ("updateInfo".equals(action)) {
            User userToUpdate = userService.getUserById(sessionUser.getId());
            userToUpdate.setRealName(request.getParameter("realName"));
            userToUpdate.setPhone(request.getParameter("phone"));
            userToUpdate.setWechat(request.getParameter("wechat"));
            userToUpdate.setQq(request.getParameter("qq"));
            userToUpdate.setDormitory(request.getParameter("dormitory"));
            userToUpdate.setClassRole(request.getParameter("classRole"));
            userToUpdate.setBio(request.getParameter("bio"));
            
            String gender = request.getParameter("gender");
            if(gender != null) userToUpdate.setGender(Integer.parseInt(gender));
            
            boolean success = userService.updateProfile(userToUpdate, ipAddress);
            if(success) session.setAttribute("sessionUser", userService.getUserById(sessionUser.getId()));
            response.sendRedirect(request.getContextPath() + "/profile");

        } else if ("updatePrivacy".equals(action)) {
            int phonePrivacy = Integer.parseInt(request.getParameter("privacyPhone"));
            int wechatPrivacy = Integer.parseInt(request.getParameter("privacyWechat"));
            int qqPrivacy = Integer.parseInt(request.getParameter("privacyQq"));
            
            userService.updatePrivacySettings(sessionUser.getId(), phonePrivacy, wechatPrivacy, qqPrivacy, ipAddress);
            session.setAttribute("sessionUser", userService.getUserById(sessionUser.getId()));
            response.sendRedirect(request.getContextPath() + "/profile");
            
        } else if ("changePwd".equals(action)) {
            String oldPwd = request.getParameter("oldPassword");
            String newPwd = request.getParameter("newPassword");
            boolean success = userService.changePassword(sessionUser.getId(), oldPwd, newPwd, ipAddress);
            if (success) {
                // 修改密码成功后，在 Session 埋入提示，重定向到登录页或重新登录
                session.invalidate(); // 销毁旧会话
                request.getSession().setAttribute("loginError", "🎉 密码修改成功！请使用新密码重新登录。");
                response.sendRedirect(request.getContextPath() + "/login");
            } else {
                // 修改失败，传回原密码错误提示
                request.setAttribute("errorMsg", "修改失败：原密码输入错误！");
                doGet(request, response);
            }
        }
    }
}