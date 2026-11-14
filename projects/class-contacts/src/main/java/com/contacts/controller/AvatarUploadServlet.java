package com.contacts.controller;

import com.contacts.entity.User;
import com.contacts.service.UserService;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;
import javax.servlet.ServletException;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

@WebServlet("/avatarUpload")
@MultipartConfig(maxFileSize = 5242880) // 限制 5MB
public class AvatarUploadServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private UserService userService = new UserService();
    
    // 定位到服务器绝对独立路径，不受 Tomcat 重新部署影响
    private static final String SAVE_DIR = "D:/class_system_uploads/avatars";

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        if (sessionUser == null) {
            response.sendRedirect(request.getContextPath() + "/login");
            return;
        }

        Part part = request.getPart("avatarFile");
        String fileName = part.getSubmittedFileName();
        if (fileName != null && !fileName.trim().isEmpty()) {
            String ext = fileName.substring(fileName.lastIndexOf(".")).toLowerCase();
            if (".jpg".equals(ext) || ".png".equals(ext) || ".jpeg".equals(ext) || ".gif".equals(ext)) {
                
                // 【安全增强】简单检查文件头部魔数，防止木马伪装后缀
                if (!isImageFile(part.getInputStream())) {
                    request.setAttribute("errorMsg", "非法图片文件格式！");
                    request.getRequestDispatcher("/jsp/user-profile.jsp").forward(request, response);
                    return;
                }

                String newFileName = "avatar_" + sessionUser.getId() + "_" + UUID.randomUUID().toString().substring(0, 8) + ext;
                
                File dir = new File(SAVE_DIR);
                if (!dir.exists()) dir.mkdirs();

                // 物理保存到外部目录
                part.write(SAVE_DIR + File.separator + newFileName);

                // 更新数据库
                userService.uploadAvatar(sessionUser.getId(), newFileName, request.getRemoteAddr());
                
                // 同步更新 Session 中的状态与真实对象
                sessionUser.setAvatar(newFileName);
                session.setAttribute("sessionUser", sessionUser);
            }
        }
        response.sendRedirect(request.getContextPath() + "/profile");
    }

    // 基础文件头魔数验证
    private boolean isImageFile(InputStream in) throws IOException {
        byte[] b = new byte[4];
        in.read(b, 0, b.length);
        String type = bytesToHexString(b).toUpperCase();
        return type.contains("FFD8FF") || type.contains("89504E47") || type.contains("47494638");
    }
    
    private String bytesToHexString(byte[] src) {
        StringBuilder stringBuilder = new StringBuilder();
        if (src == null || src.length <= 0) return null;
        for (byte aSrc : src) {
            int v = aSrc & 0xFF;
            String hv = Integer.toHexString(v);
            if (hv.length() < 2) stringBuilder.append(0);
            stringBuilder.append(hv);
        }
        return stringBuilder.toString();
    }
}