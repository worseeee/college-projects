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

@WebServlet("/contacts")
public class ContactListServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private UserService userService = new UserService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        String keyword = request.getParameter("keyword");
        
        List<User> fullList = userService.searchUsers(keyword, sessionUser.getId());
        
        // 分页逻辑处理 (前端传入 page 参数)
        String pageStr = request.getParameter("page");
        int page = (pageStr == null || pageStr.isEmpty()) ? 1 : Integer.parseInt(pageStr);
        int pageSize = 15;
        int totalRecords = fullList.size();
        int totalPages = (int) Math.ceil((double) totalRecords / pageSize);
        
        if (page < 1) page = 1;
        if (page > totalPages && totalPages > 0) page = totalPages;
        
        int fromIndex = (page - 1) * pageSize;
        int toIndex = Math.min(fromIndex + pageSize, totalRecords);
        List<User> pagedList = fullList.subList(fromIndex, toIndex);
        
        request.setAttribute("contactList", pagedList);
        request.setAttribute("currentPage", page);
        request.setAttribute("totalPages", totalPages);
        request.setAttribute("keyword", keyword == null ? "" : keyword);
        
        request.getRequestDispatcher("/jsp/contact-list.jsp").forward(request, response);
    }
}