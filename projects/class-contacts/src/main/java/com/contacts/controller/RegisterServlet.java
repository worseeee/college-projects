package com.contacts.controller;

import com.contacts.entity.User;
import com.contacts.service.UserService;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/register")
public class RegisterServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private UserService userService = new UserService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.getRequestDispatcher("/jsp/register.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        
        String studentNo = request.getParameter("studentNo");
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        String realName = request.getParameter("realName");
        String phone = request.getParameter("phone");
        String email = request.getParameter("email");
        String genderStr = request.getParameter("gender");
        
        if (studentNo == null || username == null || password == null || realName == null) {
            request.setAttribute("errorMsg", "必填项不能为空");
            request.getRequestDispatcher("/jsp/register.jsp").forward(request, response);
            return;
        }

        User user = new User();
        user.setStudentNo(studentNo);
        user.setUsername(username);
        user.setPassword(password);
        user.setRealName(realName);
        user.setPhone(phone);
        user.setEmail(email);
        user.setGender(genderStr != null && !genderStr.isEmpty() ? Integer.parseInt(genderStr) : 0);
        user.setStatus(0);
        user.setRole(1);
        user.setAvatar("default.png");
        
        user.setPrivacyPhone(0);
        user.setPrivacyWechat(0);
        user.setPrivacyQq(0);

        boolean success = userService.register(user, request.getRemoteAddr());

        if (success) {
            request.setAttribute("errorMsg", "注册成功，请等待管理员审核");
            request.getRequestDispatcher("/jsp/login.jsp").forward(request, response);
        } else {
            request.setAttribute("errorMsg", "注册失败，学号或账号可能已存在");
            request.getRequestDispatcher("/jsp/register.jsp").forward(request, response);
        }
    }
}