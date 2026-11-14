package com.contacts.controller;

import com.contacts.entity.User;
import com.contacts.service.FriendshipService;
import com.contacts.service.UserService;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

@WebServlet("/userDetail")
public class UserDetailServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private UserService userService = new UserService();
    private FriendshipService friendshipService = new FriendshipService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        
        String idParam = request.getParameter("id");
        if (idParam == null || idParam.trim().isEmpty()) {
            response.sendRedirect(request.getContextPath() + "/contacts");
            return;
        }
        
        int targetUserId = Integer.parseInt(idParam);
        
        // 1. 获取目标用户的脱敏前基础对象
        User targetUser = userService.getUserById(targetUserId);
        if (targetUser == null) {
            response.sendRedirect(request.getContextPath() + "/contacts");
            return;
        }

        // 2. 核心架构逻辑：根据两者的好友纽带状态进行隐私降级/脱敏控制
        boolean isFriend = friendshipService.isFriend(sessionUser.getId(), targetUserId);
        boolean isSelf = (sessionUser.getId() == targetUserId);
        
        // 执行安全脱敏过滤
        if (!isSelf && !isFriend) {
            if (targetUser.getPrivacyPhone() == 1 || targetUser.getPrivacyPhone() == 2) {
                targetUser.setPhone("仅好友或本人可见");
            }
            if (targetUser.getPrivacyWechat() == 1 || targetUser.getPrivacyWechat() == 2) {
                targetUser.setWechat("仅好友或本人可见");
            }
            if (targetUser.getPrivacyQq() == 1 || targetUser.getPrivacyQq() == 2) {
                targetUser.setQq("仅好友或本人可见");
            }
        } else if (!isSelf && isFriend) {
            if (targetUser.getPrivacyPhone() == 2) targetUser.setPhone("仅本人可见");
            if (targetUser.getPrivacyWechat() == 2) targetUser.setWechat("仅本人可见");
            if (targetUser.getPrivacyQq() == 2) targetUser.setQq("仅本人可见");
        }

        // 3. 计算按钮状态矩阵码
        int relationStatus = 0; // 默认毫无干系，可申请
        if (isSelf) {
            relationStatus = -1; // 自己本人
        } else if (isFriend) {
            relationStatus = 1;  // 正式好友，可私聊、可删除
        } else {
            // 深入排查是否处于挂起审核状态
            if (friendshipService.hasSentRequest(sessionUser.getId(), targetUserId)) {
                relationStatus = 2; // 我已经向对方发送了申请，等待中
            } else if (friendshipService.hasSentRequest(targetUserId, sessionUser.getId())) {
                relationStatus = 3; // 对方加我，我有待审批项
            }
        }

        request.setAttribute("targetUser", targetUser);
        request.setAttribute("relationStatus", relationStatus);
        
        // 提取闪现消息反馈
        if (session.getAttribute("flashMsg") != null) {
            request.setAttribute("flashMsg", session.getAttribute("flashMsg"));
            request.setAttribute("flashType", session.getAttribute("flashType"));
            session.removeAttribute("flashMsg");
            session.removeAttribute("flashType");
        }

        request.getRequestDispatcher("/jsp/user-detail.jsp").forward(request, response);
    }
}