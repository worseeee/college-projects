package com.contacts.controller;

import com.contacts.entity.Friendship;
import com.contacts.entity.User;
import com.contacts.service.FriendshipService;

import java.io.IOException;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

/**
 * 好友模块控制器（核心重构版：引入 Flash Message 用户操作反馈机制）
 */
@WebServlet("/friendship")
public class FriendshipServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private FriendshipService friendshipService = new FriendshipService();

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

        // 1. 列表展示大厅：同时负责负责将 Session 中的闪现提示转交至 Request 域，方便一次性渲染
        if (action == null || "list".equals(action)) {
            // 获取已通过的好友
            List<Friendship> friends = friendshipService.getFriendList(sessionUser.getId());
            // 获取待我审核的好友申请 (status = 0)
            List<Friendship> pendingRequests = friendshipService.getPendingRequests(sessionUser.getId());
            
            request.setAttribute("friends", friends);
            request.setAttribute("pendingRequests", pendingRequests);
            
            // 【核心技巧：Flash Message 读取与即焚】
            // 如果 Session 中存在跳转前留下的提示语，提取到 Request 域给前端呈现，随后立刻从 Session 移除
            if (session.getAttribute("flashMsg") != null) {
                request.setAttribute("flashMsg", session.getAttribute("flashMsg"));
                request.setAttribute("flashType", session.getAttribute("flashType"));
                session.removeAttribute("flashMsg");
                session.removeAttribute("flashType");
            }

            request.getRequestDispatcher("/jsp/friend-list.jsp").forward(request, response);
            return;
            
        // 2. 发起好友申请
        } else if ("add".equals(action)) {
            int friendId = Integer.parseInt(request.getParameter("friendId"));
            int result = friendshipService.sendFriendRequest(sessionUser.getId(), friendId, ipAddress);
            
            // 【核心修复】根据业务层返回的不同状态码，设定 Session 级别的单次闪现提示框 (Toast / Alert)
            String alertMsg;
            String alertType;
            switch (result) {
                case 1:  alertMsg = "好友申请发送成功，等待对方验证！"; alertType = "success"; break;
                case -1: alertMsg = "系统拦截：请勿添加您自己为好友！"; alertType = "warning"; break;
                case -2: alertMsg = "你们已经是亲密好友啦，不需要重复添加！"; alertType = "info"; break;
                case -3: alertMsg = "申请正在等待对方处理中，请勿重复发起！"; alertType = "warning"; break;
                default: alertMsg = "服务器开小差了，申请发送失败！"; alertType = "danger"; break;
            }
            // 利用 Session 传递临时消息，防止重定向(Redirect)后 Request 域数据丢失
            session.setAttribute("flashMsg", alertMsg);
            session.setAttribute("flashType", alertType);
            
            response.sendRedirect(request.getContextPath() + "/userDetail?id=" + friendId);
            return;
            
        // 3. 同意好友申请
        } else if ("accept".equals(action)) {
            int requesterId = Integer.parseInt(request.getParameter("requesterId"));
            boolean success = friendshipService.auditFriendRequest(sessionUser.getId(), requesterId, 1, ipAddress);
            
            if (success) {
                session.setAttribute("flashMsg", "已成功添加为好友！可以开始聊天啦~");
                session.setAttribute("flashType", "success");
            } else {
                session.setAttribute("flashMsg", "同意申请失败，请稍后再试。");
                session.setAttribute("flashType", "danger");
            }
            response.sendRedirect(request.getContextPath() + "/friendship?action=list");
            return;
            
        // 4. 拒绝好友申请
        } else if ("reject".equals(action)) {
            int requesterId = Integer.parseInt(request.getParameter("requesterId"));
            boolean success = friendshipService.auditFriendRequest(sessionUser.getId(), requesterId, 2, ipAddress);
            
            if (success) {
                session.setAttribute("flashMsg", "已委婉拒绝了对方的好友申请。");
                session.setAttribute("flashType", "info");
            } else {
                session.setAttribute("flashMsg", "操作处理失败。");
                session.setAttribute("flashType", "danger");
            }
            response.sendRedirect(request.getContextPath() + "/friendship?action=list");
            return;
            
        // 5. 删除好友
        } else if ("delete".equals(action)) {
            int friendId = Integer.parseInt(request.getParameter("friendId"));
            boolean success = friendshipService.removeFriend(sessionUser.getId(), friendId, ipAddress);
            
            if (success) {
                session.setAttribute("flashMsg", "好友关系已解除。");
                session.setAttribute("flashType", "warning");
            } else {
                session.setAttribute("flashMsg", "删除好友失败！");
                session.setAttribute("flashType", "danger");
            }
            response.sendRedirect(request.getContextPath() + "/friendship?action=list");
            return;
        }
    }
}