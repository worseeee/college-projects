package com.contacts.controller;

import com.contacts.entity.Announcement;
import com.contacts.entity.User;
import com.contacts.service.AnnouncementService;
import com.contacts.dao.AnnouncementDao;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.List;
import java.util.UUID;
import javax.servlet.ServletException;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

@WebServlet("/announcement")
@MultipartConfig(maxFileSize = 20971520) // 支持 20MB 原始附件
public class AnnouncementServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private AnnouncementService announcementService = new AnnouncementService();
    private AnnouncementDao announcementDao = new AnnouncementDao();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");

        List<Announcement> announcements = announcementService.getValidAnnouncements();
        int totalClassUsers = announcementDao.getTotalUserCount();

        for (Announcement a : announcements) {
            if ("作业".equals(a.getCategory())) {
                // 作业模式：统计已交/未交
                int submitted = announcementDao.getSubmittedCount(a.getId());
                a.setSubmittedCount(submitted);
                a.setUnsubmittedCount(Math.max(0, totalClassUsers - submitted));
            } else {
                // 通知模式：统计已读/未读
                if (sessionUser != null) {
                    announcementDao.markAsRead(a.getId(), sessionUser.getId());
                }
                int reads = announcementDao.getReadCount(a.getId());
                a.setReadCount(reads);
                a.setUnreadCount(Math.max(0, totalClassUsers - reads));
            }
        }

        request.setAttribute("announcements", announcements);
        request.getRequestDispatcher("/jsp/announcement.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        String action = request.getParameter("action");
        if (action == null) action = "add";
        
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");

        if ("add".equals(action)) {
            Announcement a = new Announcement();
            a.setAdminId(sessionUser.getId());
            a.setTitle(request.getParameter("title"));
            a.setContent(request.getParameter("content"));
            a.setCategory(request.getParameter("category")); // 接收前端是"通知"还是"作业"
            
            String isTopStr = request.getParameter("isTop");
            a.setIsTop((isTopStr == null || isTopStr.isEmpty()) ? 0 : Integer.parseInt(isTopStr));
            
            String expireStr = request.getParameter("expireTime");
            if (expireStr != null && !expireStr.trim().isEmpty()) {
                try {
                    a.setExpireTime(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm").parse(expireStr.replace("T", " ").trim()));
                } catch (Exception e) {}
            }

            // 处理发布人上传的公告/作业原始附件
            Part part = request.getPart("attachment");
            if (part != null && part.getSize() > 0) {
                String originalName = part.getSubmittedFileName();
                String ext = originalName.substring(originalName.lastIndexOf("."));
                String newName = "ann_doc_" + UUID.randomUUID().toString().substring(0, 8) + ext;
                String savePath = request.getServletContext().getRealPath("/upload");
                File dir = new File(savePath);
                if (!dir.exists()) dir.mkdirs();
                part.write(savePath + File.separator + newName);
                a.setAttachmentUrl("upload/" + newName);
            }

            announcementDao.addAnnouncementWithAttachment(a);
        }
        response.sendRedirect(request.getContextPath() + "/announcement");
    }
}