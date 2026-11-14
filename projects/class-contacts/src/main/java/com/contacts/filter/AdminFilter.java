package com.contacts.filter;

import com.contacts.entity.User;

import java.io.IOException;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebFilter(urlPatterns = {"/announcement", "/homework", "/activity"})
public class AdminFilter implements Filter {
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {}

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse resp = (HttpServletResponse) response;
        
        // 【核心绝杀修复】因为 AdminFilter 按字母排序会比 CharacterEncodingFilter 先执行！
        // 必须在调用 req.getParameter("action") 之前，强行设置 UTF-8 编码，否则 Tomcat 会以 ISO-8859-1 永久锁定表单！
        req.setCharacterEncoding("UTF-8");
        resp.setCharacterEncoding("UTF-8");
        
        String action = req.getParameter("action");
        if ("add".equals(action) || "delete".equals(action)) {
            User sessionUser = (User) req.getSession().getAttribute("sessionUser");
            // 【权限下放升级】role == 2 是管理员；can_publish_announcement == 1 是被赋予发公告权限的老师/课代表
            boolean hasPermission = (sessionUser != null) && 
                (sessionUser.getRole() == 2 || sessionUser.getCanPublishAnnouncement() == 1);
                
            if (!hasPermission) {
                resp.setContentType("text/html;charset=UTF-8");
                resp.getWriter().write("<script>alert('抱歉，您没有发布公告的权限！');history.back();</script>");
                return;
            }
        }
        chain.doFilter(request, response);
    }
    
    @Override
    public void destroy() {}
}