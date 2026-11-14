package com.contacts.controller;

import com.contacts.entity.PrivateMessage;
import com.contacts.entity.User;
import com.contacts.service.PrivateMessageService;
import com.contacts.service.UserService;

import java.io.IOException;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

/**
 * 私信模块控制器（核心重构版：接入业务校验结果与显式错误渲染机制）
 */
@WebServlet("/message")
public class PrivateMessageServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private PrivateMessageService messageService = new PrivateMessageService();
    private UserService userService = new UserService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doPost(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        String action = request.getParameter("action");
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        String ipAddress = request.getRemoteAddr();

        // ==================== 1. 会话大厅列表 ====================
        if (action == null || "list".equals(action)) {
            // 获取所有有过私聊痕迹的会话卡片列表（已完整适配上一轮的 List<PrivateMessage> 升级）
            List<PrivateMessage> sessionChats = messageService.getChatSessionList(sessionUser.getId());
            request.setAttribute("sessionChats", sessionChats);
            request.getRequestDispatcher("/jsp/message-list.jsp").forward(request, response);
            return;
            
        // ==================== 2. 进入具体私聊对话框 ====================
        } else if ("chat".equals(action)) {
            int targetId = Integer.parseInt(request.getParameter("targetId"));
            
            // 自动标记当前对话为已读
            messageService.markAsRead(targetId, sessionUser.getId());
            
            // 获取历史记录与对端用户详情
            List<PrivateMessage> history = messageService.getChatHistory(sessionUser.getId(), targetId);
            request.setAttribute("chatHistory", history);
            request.setAttribute("targetUser", userService.getUserById(targetId));
            
            // 【核心技巧：从 Session 提取错误提示语并单次显式吐露至 Request 域】
            if (session.getAttribute("chatError") != null) {
                request.setAttribute("chatError", session.getAttribute("chatError"));
                session.removeAttribute("chatError"); // 即阅即焚，防止刷新页面重复提示
            }
            
            request.getRequestDispatcher("/jsp/private-message.jsp").forward(request, response);
            return;
            
        // ==================== 3. 发送私信（核心重构分支） ====================
        } else if ("send".equals(action)) {
            int targetId = Integer.parseInt(request.getParameter("targetId"));
            String content = request.getParameter("content");
            
            // 严禁发送空文本造成数据库死记录与视觉污染
            if (content == null || content.trim().isEmpty()) {
                session.setAttribute("chatError", "不能发送空消息哟！");
                response.sendRedirect(request.getContextPath() + "/message?action=chat&targetId=" + targetId);
                return;
            }

            // 调用升级后的 API 获取业务状态详情文本 (转调上一轮在 Service 写好的字符串返回接口)
            String resultMsg = messageService.sendPrivateMessage(sessionUser.getId(), targetId, content.trim());
            
            if ("SUCCESS".equals(resultMsg)) {
                // 发送成功，清除可能存留的历史错误并正常重定向
                session.removeAttribute("chatError");
            } else {
                // 【关键修复】发生非好友拦截等问题时，将具体原因抛至会话中让前端吐露
                session.setAttribute("chatError", "⚠️ 发送拦截：" + resultMsg);
            }
            response.sendRedirect(request.getContextPath() + "/message?action=chat&targetId=" + targetId);
            return;
            
        // ==================== 4. 获取未读消息总计（供前端小红点使用） ====================
        } else if ("unreadCount".equals(action)) {
            int count = messageService.getUnreadCount(sessionUser.getId());
            response.setContentType("text/plain");
            response.getWriter().write(String.valueOf(count));
            return;
            
        // ==================== 5. 清空聊天记录 ====================
        } else if ("clear".equals(action)) {
            int targetId = Integer.parseInt(request.getParameter("targetId"));
            messageService.clearConversation(sessionUser.getId(), targetId, ipAddress);
            
            // 友善给出一个清空成功的提示
            session.setAttribute("chatError", "💡 聊天记录已清空");
            response.sendRedirect(request.getContextPath() + "/message?action=chat&targetId=" + targetId);
            return;
        }
    }
}