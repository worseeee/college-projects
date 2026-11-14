package com.contacts.controller;

import com.contacts.entity.Homework;
import com.contacts.entity.User;
import com.contacts.service.HomeworkService;

import java.io.IOException;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

@WebServlet("/homework")
public class HomeworkServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private HomeworkService homeworkService = new HomeworkService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        
        String action = request.getParameter("action");
        
        if ("download".equals(action)) {
            // 附件流式物理下载模拟引擎
            String filename = request.getParameter("filename");
            if (filename == null || filename.trim().isEmpty()) return;
            
            response.setContentType("application/octet-stream");
            response.setHeader("Content-Disposition", "attachment; filename=" + java.net.URLEncoder.encode(filename, "UTF-8"));
            
            // 优雅输出模拟作业模板文本字节流，避免文件 IO 报错
            response.getWriter().write("【系统提示】这是作业附件 [" + filename + "] 的模拟下发内容，包含本门课程设计的大纲要求。");
            return;
        }

        // 默认列表行为
        List<Homework> homeworkList = homeworkService.getAllHomeworks();
        request.setAttribute("homeworkList", homeworkList);
        request.getRequestDispatcher("/jsp/homework.jsp").forward(request, response);
    }
}