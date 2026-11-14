package servlet;

import entity.FileInfo;
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.MultipartConfig;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.Part;

@WebServlet("/upload")
// 开启多部件表单支持，限制单文件10MB，总请求50MB
@MultipartConfig(maxFileSize = 10485760, maxRequestSize = 52428800)
public class UploadServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        // 1. 设置请求和响应编码（防乱码）
        request.setCharacterEncoding("UTF-8");
        response.setContentType("text/html;charset=UTF-8");

        try {
            // 2. 接收普通表单数据：用户名
            String username = request.getParameter("username");
            if (username == null || username.trim().isEmpty()) {
                username = "匿名用户";
            }
            // 利用 session 保存当前用户，方便下次自动填写
            request.getSession().setAttribute("currentUsername", username);

            // 3. 接收文件 Part
            Part filePart = request.getPart("file");
            // Tomcat 8+ 支持 getSubmittedFileName
            String fileName = filePart.getSubmittedFileName();

            if (fileName == null || fileName.trim().isEmpty()) {
                throw new RuntimeException("请选择要上传的文件！");
            }

            // 4. 确定上传物理目录（放在 WebContent/upload 下）
            String uploadPath = request.getServletContext().getRealPath("/upload");
            File uploadDir = new File(uploadPath);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs(); // 若目录不存在则自动创建
            }

            // 5. 将文件写入磁盘
            filePart.write(uploadPath + File.separator + fileName);

            // 6. 收集并格式化文件信息
            String uploadTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
            String fileSizeStr = formatFileSize(filePart.getSize());
            FileInfo fileInfo = new FileInfo(fileName, username, uploadTime, fileSizeStr, "upload/" + fileName);

            // 7. 将文件信息存入 Application 全局作用域 (线程安全处理)
            synchronized (this) {
                @SuppressWarnings("unchecked")
                List<FileInfo> fileList = (List<FileInfo>) request.getServletContext().getAttribute("globalFileList");
                if (fileList == null) {
                    fileList = new ArrayList<>();
                }
                // 插入到列表首位，保证最新上传的在最前面
                fileList.add(0, fileInfo); 
                request.getServletContext().setAttribute("globalFileList", fileList);
            }

            // 8. 转发到结果页面
            request.setAttribute("msg", "上传成功！");
            request.setAttribute("status", "success");
            request.getRequestDispatcher("/uploadResult.jsp").forward(request, response);

        } catch (Exception e) {
            e.printStackTrace();
            request.setAttribute("msg", "上传失败：" + e.getMessage());
            request.setAttribute("status", "error");
            request.getRequestDispatcher("/uploadResult.jsp").forward(request, response);
        }
    }

    // 辅助方法：将字节转换为易读的 KB/MB 格式
    private String formatFileSize(long size) {
        if (size < 1024) return size + " B";
        int z = (63 - Long.numberOfLeadingZeros(size)) / 10;
        return String.format("%.2f %sB", (double)size / (1L << (z*10)), " KMGTPE".charAt(z));
    }
}