package com.contacts.controller;

import com.contacts.dao.BookmarkDao;
import com.contacts.entity.User;
import java.io.IOException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

@WebServlet("/bookmark")
public class BookmarkServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private BookmarkDao bookmarkDao = new BookmarkDao();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        
        String action = request.getParameter("action");
        int targetId = Integer.parseInt(request.getParameter("targetId"));
        
        if ("add".equals(action)) {
            bookmarkDao.addBookmark(sessionUser.getId(), targetId);
            session.setAttribute("flashMsg", "已成功将该同学移入常用收藏名单！");
            session.setAttribute("flashType", "success");
        } else if ("remove".equals(action)) {
            bookmarkDao.removeBookmark(sessionUser.getId(), targetId);
            session.setAttribute("flashMsg", "已将该同学从收藏夹移出。");
            session.setAttribute("flashType", "info");
        }
        
        response.sendRedirect(request.getContextPath() + "/userDetail?id=" + targetId);
    }
}