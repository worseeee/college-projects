package com.contacts.service;

import com.contacts.dao.FriendshipDao;
import com.contacts.dao.LogDao;
import com.contacts.dao.PrivateMessageDao;
import com.contacts.entity.PrivateMessage;
import com.contacts.entity.User;

import java.util.List;

/**
 * 私信模块业务逻辑层（已接入好友关系校验与日志审计）
 */
public class PrivateMessageService {
    
    private PrivateMessageDao msgDao = new PrivateMessageDao();
    private FriendshipDao friendDao = new FriendshipDao();
    private LogDao logDao = new LogDao();

    /**
     * 解决编译错误的核心方法：获取当前用户的聊天会话大厅列表
     */
    public List<PrivateMessage> getChatSessionList(Integer userId) {
        if (userId == null) return null;
        return msgDao.getChatSessionList(userId);
    }

    /**
     * 升级版核心业务：带社交规约校验的发送私信逻辑
     * @return 业务执行状态提示语 (返回 "SUCCESS" 代表成功)
     */
    public String sendPrivateMessage(int senderId, int receiverId, String content) {
        if (senderId == receiverId) {
            return "不能给自己发送私信！";
        }
        
        // 【核心规约验收】强制检查是否为好友
        if (!friendDao.isFriend(senderId, receiverId)) {
            return "仅支持向好友发送私信，请先发起好友申请！";
        }

        PrivateMessage msg = new PrivateMessage();
        msg.setSenderId(senderId);
        msg.setReceiverId(receiverId);
        msg.setContent(content);
        
        boolean success = msgDao.sendMessage(msg);
        return success ? "SUCCESS" : "消息发送失败，请稍后重试。";
    }

    /**
     * 向下兼容历史 Servlet 的发送重载方法（自带 IP 审计与好友过滤）
     */
    public boolean sendMessage(int senderId, int receiverId, String content, String ipAddress) {
        String result = sendPrivateMessage(senderId, receiverId, content);
        if ("SUCCESS".equals(result)) {
            return true;
        } else {
            // 如果因为非好友被拦截，记录日志以便安全审计
            if (logDao != null && ipAddress != null) {
                logDao.addLog(senderId, "尝试向非好友(ID:" + receiverId + ")发送私信被系统拦截", ipAddress);
            }
            return false;
        }
    }

    /**
     * 获取两人的聊天历史记录
     */
    public List<PrivateMessage> getChatHistory(int userId1, int userId2) {
        return msgDao.getChatHistory(userId1, userId2);
    }

    /**
     * 标记某个回话的所有未读消息为已读
     */
    public boolean markAsRead(int senderId, int receiverId) {
        return msgDao.markAsRead(senderId, receiverId);
    }

    /**
     * 获取当前用户的未读私信总数
     */
    public int getUnreadCount(int currentUserId) {
        return msgDao.getUnreadCount(currentUserId);
    }

    /**
     * 清空与某个人的全部双向对话（带操作审计日志）
     */
    public boolean clearConversation(int userId, int targetId, String ipAddress) {
        if (logDao != null) {
            logDao.addLog(userId, "清空了与用户ID为 " + targetId + " 的全部聊天记录", ipAddress);
        }
        return msgDao.clearConversation(userId, targetId);
    }
}