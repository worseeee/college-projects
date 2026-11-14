package com.contacts.controller;

import com.contacts.entity.BoardMessage;
import com.contacts.entity.User;
import com.contacts.service.BoardService;

import java.io.IOException;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/board")
public class BoardServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private BoardService boardService = new BoardService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String action = request.getParameter("action");
        
        // 【新增】如果请求是查看详情与回复
        if ("detail".equals(action)) {
            int msgId = Integer.parseInt(request.getParameter("id"));
            // 1. 获取主贴详情
            BoardMessage mainMsg = boardService.getMessageById(msgId);
            // 2. 获取主贴下的所有回复帖子 (parentId = msgId)
            List<BoardMessage> replies = boardService.getReplies(msgId);
            
            request.setAttribute("mainMsg", mainMsg);
            request.setAttribute("replies", replies);
            request.getRequestDispatcher("/jsp/board-detail.jsp").forward(request, response);
            return;
        }

        // --- 以下为原有的默认大厅列表逻辑，保持不变 ---
        String pageStr = request.getParameter("page");
        int page = (pageStr == null || pageStr.isEmpty()) ? 1 : Integer.parseInt(pageStr);
        int limit = 20;
        int offset = (page - 1) * limit;

        List<BoardMessage> mainMsgs = boardService.getMainMessages(offset, limit);
        for (BoardMessage msg : mainMsgs) {
            msg.setReplies(boardService.getReplies(msg.getId()));
        }
        
        request.setAttribute("boardList", mainMsgs);
        request.setAttribute("currentPage", page);
        request.getRequestDispatcher("/jsp/board.jsp").forward(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        String action = request.getParameter("action");
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        String ipAddress = request.getRemoteAddr();

        if ("publish".equals(action)) {
            String content = request.getParameter("content");
            String parentIdStr = request.getParameter("parentId");
            int parentId = (parentIdStr == null || parentIdStr.isEmpty()) ? 0 : Integer.parseInt(parentIdStr);
            
            boardService.publishMessage(sessionUser.getId(), content, parentId, ipAddress);
            response.sendRedirect(request.getContextPath() + "/board");
            
        } else if ("delete".equals(action)) {
            int messageId = Integer.parseInt(request.getParameter("messageId"));
            boardService.deleteMessage(messageId, sessionUser.getId(), sessionUser.getRole(), ipAddress);
            response.sendRedirect(request.getContextPath() + "/board");
            
        } else if ("like".equals(action)) {
            int messageId = Integer.parseInt(request.getParameter("messageId"));
            // 接收参数判断用户是在“留言大厅”还是“详情页”点的赞
            String source = request.getParameter("source"); 
            
            String result = boardService.likeMessage(messageId, sessionUser.getId());
            if ("ALREADY_LIKED".equals(result)) {
                // 使用 Session 抛出 Toast 警告
                session.setAttribute("flashMsg", "您已经赞过这条留言啦！");
            }
            
            // 智能返回：在哪里点的赞，就刷新回哪个页面
            if ("detail".equals(source)) {
                response.sendRedirect(request.getContextPath() + "/board?action=detail&id=" + messageId);
            } else {
                response.sendRedirect(request.getContextPath() + "/board");
            }
        }
    }
}