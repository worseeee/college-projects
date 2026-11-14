package servlet;

import entity.FileInfo;
import java.io.IOException;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/list")
public class FileListServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        // 核心：直接读取 Application 作用域中的列表
        @SuppressWarnings("unchecked")
        List<FileInfo> fileList = (List<FileInfo>) request.getServletContext().getAttribute("globalFileList");
        
        // 传递给 request 以供当前页面渲染
        request.setAttribute("fileList", fileList);
        
        // 内部转发给 fileList.jsp 页面片段渲染
        request.getRequestDispatcher("/fileList.jsp").forward(request, response);
    }
}