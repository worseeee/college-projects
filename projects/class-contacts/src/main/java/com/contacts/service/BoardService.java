package com.contacts.service;

import com.contacts.dao.BoardMessageDao;
import com.contacts.dao.LogDao;
import com.contacts.dao.SensitiveWordDao;
import com.contacts.entity.BoardMessage;

import java.util.List;

public class BoardService {

    private BoardMessageDao boardDao = new BoardMessageDao();
    private SensitiveWordDao sensitiveWordDao = new SensitiveWordDao();
    private LogDao logDao = new LogDao();

    public int publishMessage(int userId, String content, int parentId, String ipAddress) {
        if (sensitiveWordDao.containsSensitiveWord(content)) {
            logDao.addLog(userId, "发布留言包含敏感词被拦截", ipAddress);
            return -1;
        }
        
        if (parentId != 0) {
            BoardMessage parentMsg = boardDao.getMessageById(parentId);
            if (parentMsg == null) return -2; // 父留言不存在
        }
        
        boolean success = boardDao.addMessage(userId, content, parentId);
        if (success) {
            logDao.addLog(userId, "发布了班级留言", ipAddress);
            return 1;
        }
        return 0;
    }

    public boolean deleteMessage(int messageId, int userId, int role, String ipAddress) {
        BoardMessage msg = boardDao.getMessageById(messageId);
        if (msg == null) return false;
        
        // 权限校验：只能删除自己的留言，或者管理员(role=2)可以删除任何人的
        if (msg.getUserId() != userId && role != 2) {
            logDao.addLog(userId, "尝试越权删除留言被拦截", ipAddress);
            return false;
        }
        
        boolean success = boardDao.deleteMessage(messageId);
        if (success) {
            logDao.addLog(userId, "删除了留言ID: " + messageId, ipAddress);
        }
        return success;
    }

 // 将原来的 public boolean likeMessage(int messageId) 替换为以下代码：
    public String likeMessage(int messageId, int userId) {
        boolean success = boardDao.incrementLike(messageId, userId);
        return success ? "SUCCESS" : "ALREADY_LIKED";
    }

    public List<BoardMessage> getMainMessages(int offset, int limit) {
        return boardDao.getMainMessages(offset, limit);
    }

    public List<BoardMessage> getReplies(int parentId) {
        return boardDao.getRepliesByParentId(parentId);
    }

    public BoardMessage getMessageById(int id) {
        return boardDao.getMessageById(id);
    }
}