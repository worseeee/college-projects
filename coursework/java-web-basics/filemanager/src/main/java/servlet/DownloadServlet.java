package servlet;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.URLEncoder;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/download")
public class DownloadServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        // 1. 获取要下载的文件名
        String fileName = request.getParameter("fileName");
        if (fileName == null || fileName.trim().isEmpty()) {
            response.getWriter().write("非法的文件名！");
            return;
        }

        // 2. 找到服务器上该文件的绝对物理路径
        String uploadPath = request.getServletContext().getRealPath("/upload");
        File file = new File(uploadPath + File.separator + fileName);

        if (!file.exists()) {
            response.setContentType("text/html;charset=UTF-8");
            response.getWriter().write("<script>alert('抱歉，该文件已被删除或不存在！');history.back();</script>");
            return;
        }

        // 3. 设置下载的 MIME 类型为二进制流
        response.setContentType("application/octet-stream");
        
        // 4. 关键点：设置响应头 Content-Disposition。使用 URLEncoder 防止中文文件名变乱码
        String encodedFileName = URLEncoder.encode(fileName, "UTF-8");
        // 替换加号为空格，解决某些浏览器下的空格编码问题
        encodedFileName = encodedFileName.replaceAll("\\+", "%20"); 
        response.setHeader("Content-Disposition", "attachment; filename=\"" + encodedFileName + "\"");
        
        // 设置文件大小，让浏览器显示下载进度
        response.setContentLength((int) file.length());

        // 5. 开启 I/O 流，从服务器读取，向浏览器输出
        try (BufferedInputStream bis = new BufferedInputStream(new FileInputStream(file));
             BufferedOutputStream bos = new BufferedOutputStream(response.getOutputStream())) {
            
            byte[] buffer = new byte[4096]; // 4KB 缓冲区
            int len;
            while ((len = bis.read(buffer)) != -1) {
                bos.write(buffer, 0, len);
            }
            bos.flush();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}