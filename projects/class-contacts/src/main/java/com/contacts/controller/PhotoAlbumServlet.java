package com.contacts.controller;

import com.contacts.entity.PhotoAlbum;
import com.contacts.entity.User;
import com.contacts.service.PhotoAlbumService;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import javax.servlet.ServletException;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import javax.servlet.http.Part;

@WebServlet("/album")
@MultipartConfig(maxFileSize = 10485760, maxRequestSize = 52428800) // 限制10MB文件
public class PhotoAlbumServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private PhotoAlbumService photoAlbumService = new PhotoAlbumService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        List<PhotoAlbum> photos = photoAlbumService.getPhotoList();
        request.setAttribute("photos", photos);
        request.getRequestDispatcher("/jsp/album.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        String action = request.getParameter("action");
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        String ipAddress = request.getRemoteAddr();

        if ("upload".equals(action)) {
            Part part = request.getPart("file");
            String description = request.getParameter("description");
            
            String submittedFileName = part.getSubmittedFileName();
            if (submittedFileName != null && !submittedFileName.isEmpty()) {
            	String ext = submittedFileName.substring(submittedFileName.lastIndexOf(".")).toLowerCase();
            	if (!ext.equals(".jpg") && !ext.equals(".png") && !ext.equals(".jpeg") && !ext.equals(".gif")) {
            	    request.setAttribute("errorMsg", "只能上传图片格式！");
            	    request.getRequestDispatcher("/jsp/album.jsp").forward(request, response);
            	    return;
            	}
            	// 校验通过后继续执行 UUID 生成和 part.write()
                String newFileName = UUID.randomUUID().toString() + ext;
                
                String uploadPath = request.getServletContext().getRealPath("/upload/album");
                File uploadDir = new File(uploadPath);
                if (!uploadDir.exists()) uploadDir.mkdirs();
                
                part.write(uploadPath + File.separator + newFileName);
                
                PhotoAlbum photo = new PhotoAlbum();
                photo.setUserId(sessionUser.getId());
                photo.setPhotoUrl("upload/album/" + newFileName);
                photo.setDescription(description);
                
                photoAlbumService.addPhoto(photo, ipAddress);
            }
            response.sendRedirect(request.getContextPath() + "/album");
            
        } else if ("delete".equals(action)) {
            int id = Integer.parseInt(request.getParameter("id"));
            photoAlbumService.deletePhoto(id, sessionUser.getId(), sessionUser.getRole(), ipAddress);
            response.sendRedirect(request.getContextPath() + "/album");
        }
    }
}