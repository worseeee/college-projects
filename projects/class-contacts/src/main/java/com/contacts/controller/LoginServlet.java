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

@WebServlet("/login")
public class LoginServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private UserService userService = new UserService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.getRequestDispatcher("/jsp/login.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        response.setContentType("text/html;charset=UTF-8");

        String username = request.getParameter("username");
        String password = request.getParameter("password");
        String ipAddress = request.getRemoteAddr();

        if (username == null || username.trim().isEmpty() || password == null || password.trim().isEmpty()) {
            request.setAttribute("errorMsg", "账号或密码不能为空");
            request.getRequestDispatcher("/jsp/login.jsp").forward(request, response);
            return;
        }

        User user = userService.login(username, password, ipAddress);

        if (user != null) {
            if (user.getStatus() == 0) {
                request.setAttribute("errorMsg", "您的账号正在审核中，请联系班长");
                request.getRequestDispatcher("/jsp/login.jsp").forward(request, response);
                return;
            } else if (user.getStatus() == 2) {
                request.setAttribute("errorMsg", "您的账号已被禁用");
                request.getRequestDispatcher("/jsp/login.jsp").forward(request, response);
                return;
            }
            
            HttpSession session = request.getSession();
            session.setAttribute("sessionUser", user);
            response.sendRedirect(request.getContextPath() + "/contacts");
        } else {
            request.setAttribute("errorMsg", "账号或密码错误");
            request.setAttribute("inputUsername", username);
            request.getRequestDispatcher("/jsp/login.jsp").forward(request, response);
        }
    }
}