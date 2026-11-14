package com.contacts.controller;

import com.contacts.dao.AnnouncementDao;
import com.contacts.entity.Announcement;
import com.contacts.entity.AnnouncementReply;
import com.contacts.entity.User;

import javax.servlet.ServletException;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
import java.io.File;
import java.io.IOException;
import java.util.List;

@WebServlet("/announcementDetail")
@MultipartConfig(maxFileSize = 1024 * 1024 * 50) 
public class AnnouncementDetailServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private AnnouncementDao announcementDao = new AnnouncementDao();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String idParam = request.getParameter("id");
        if (idParam == null || idParam.trim().isEmpty()) {
            response.sendRedirect(request.getContextPath() + "/announcement");
            return;
        }

        int annId = Integer.parseInt(idParam);
        
        // 1. 获取公告主体
        Announcement ann = announcementDao.getAnnouncementById(annId);
        // 2. 获取这条公告下的所有回执集合
        List<AnnouncementReply> replies = announcementDao.getRepliesByAnnouncementId(annId);

        request.setAttribute("announcement", ann);
        request.setAttribute("replies", replies); // 确保 JSP 里的 c:forEach 能够遍历
        
        // 获取处理成功或失败的 Toast 闪现提示
        HttpSession session = request.getSession();
        if (session.getAttribute("flashMsg") != null) {
            request.setAttribute("flashMsg", session.getAttribute("flashMsg"));
            session.removeAttribute("flashMsg");
        }

        request.getRequestDispatcher("/jsp/announcement_detail.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");

        // ✅ 核心修复 1：参数名必须和 JSP 中的 name="announcementId" 绝对一致！
        String annIdStr = request.getParameter("announcementId");
        if (annIdStr == null || annIdStr.isEmpty()) {
            session.setAttribute("flashMsg", "❌ 提交失败：系统未捕获到表单参数！");
            response.sendRedirect(request.getContextPath() + "/announcement");
            return;
        }

        int annId = Integer.parseInt(annIdStr);
        String replyContent = request.getParameter("replyContent");

        // ✅ 核心修复 2：附件参数名必须和 JSP 中的 name="submitFile" 绝对一致！
        String fileUrl = null;
        Part filePart = request.getPart("submitFile");
        if (filePart != null && filePart.getSize() > 0) {
            // 将文件保存到 Tomcat 根目录下的 upload 文件夹
            String uploadPath = request.getServletContext().getRealPath("") + File.separator + "upload";
            File uploadDir = new File(uploadPath);
            if (!uploadDir.exists()) uploadDir.mkdir();

            String fileName = System.currentTimeMillis() + "_" + filePart.getSubmittedFileName();
            filePart.write(uploadPath + File.separator + fileName);
            fileUrl = "upload/" + fileName;
        }

        // 调用 DAO 写入数据库
        boolean success = announcementDao.addReply(annId, sessionUser.getId(), replyContent, fileUrl);

        if (success) {
            session.setAttribute("flashMsg", "✅ 回执与作业已成功提交！");
        } else {
            session.setAttribute("flashMsg", "❌ 提交失败，底层数据库异常！");
        }

        // 提交完后重定向回详情页
        response.sendRedirect(request.getContextPath() + "/announcementDetail?id=" + annId);
    }
}