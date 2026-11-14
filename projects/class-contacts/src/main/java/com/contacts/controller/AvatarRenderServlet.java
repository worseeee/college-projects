package com.contacts.controller;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * @title 外部存储头像资源安全渲染控制器
 * @description 彻底解决外部物理路径上传后前端访问 404 的隔离问题
 */
@WebServlet("/avatar/*")
public class AvatarRenderServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    // 与上传控制器保持统一的物理路径（建议后续抽取到全局 properties 配置文件）
    private static final String SAVE_DIR = "D:/class_system_uploads/avatars";

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        // 获取请求的头像文件名，例如请求 /avatar/avatar_101_xxx.jpg -> pathInfo 为 /avatar_101_xxx.jpg
        String pathInfo = request.getPathInfo();
        String fileName = (pathInfo != null && pathInfo.length() > 1) ? pathInfo.substring(1) : null;
        
        File file = null;
        if (fileName != null && !fileName.trim().isEmpty()) {
            // 【安全防御】防止目录遍历攻击 (Directory Traversal Attack: ../../etc/passwd)
            fileName = fileName.replaceAll("(\\.\\.|/|\\\\)", "");
            file = new File(SAVE_DIR, fileName);
        }

        // 如果文件不存在或请求为空，自动降级去读取 Tomcat Webapp 内部的默认头像
        if (file == null || !file.exists() || !file.isFile()) {
            String defaultAvatarPath = request.getServletContext().getRealPath("/images/default.png");
            file = new File(defaultAvatarPath);
        }

        // 设置合适的 MimeType，并开启浏览器缓存优化 (缓存 30 天)
        String mimeType = getServletContext().getMimeType(file.getName());
        if (mimeType == null) {
            mimeType = "application/octet-stream";
        }
        response.setContentType(mimeType);
        response.setContentLengthLong(file.length());
        response.setHeader("Cache-Control", "max-age=2592000, public");

        // 将外部物理文件通过 ServletOutputStream 零拷贝写入前端响应流
        try (FileInputStream fis = new FileInputStream(file);
             OutputStream os = response.getOutputStream()) {
            byte[] buffer = new byte[4096];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
            os.flush();
        }
    }
}