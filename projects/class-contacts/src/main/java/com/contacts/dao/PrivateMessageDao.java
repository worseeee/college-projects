package com.contacts.dao;

import com.contacts.entity.PrivateMessage;
import com.contacts.entity.User;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * sys_private_message 表的数据访问层（全功能完整版 - 具备高性能聚合未读统计）
 */
public class PrivateMessageDao {

    /**
     * 核心升级：聚合查询指定用户的私信大厅会话列表（增加 unread_count 精准未读条数聚合统计）
     * 利用 MySQL 子查询同时完成：最近会话归类、最新一条消息提取、以及未读红点数字计算！
     */
    public List<PrivateMessage> getChatSessionList(Integer userId) {
        List<PrivateMessage> list = new ArrayList<>();
        if (userId == null) return list;

        // 核心突破：利用 (SELECT COUNT...) 子查询，精准计算当前对方发给我的尚未阅读的消息条数
        String sql = "SELECT m1.*, u.real_name AS target_name, u.avatar AS target_avatar, " +
                     "(SELECT COUNT(*) FROM sys_private_message WHERE sender_id = u.id AND receiver_id = ? AND is_read = 0) AS unread_count " +
                     "FROM sys_private_message m1 " +
                     "INNER JOIN (" +
                     "    SELECT " +
                     "        CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END AS chat_user_id, " +
                     "        MAX(id) AS max_id " +
                     "    FROM sys_private_message " +
                     "    WHERE sender_id = ? OR receiver_id = ? " +
                     "    GROUP BY CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END" +
                     ") m2 ON m1.id = m2.max_id " +
                     "JOIN sys_user u ON u.id = m2.chat_user_id " +
                     "ORDER BY m1.create_time DESC";

        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // 为 SQL 语句注入 5 个关于当前用户 userId 的参数
            pstmt.setInt(1, userId); 
            pstmt.setInt(2, userId); 
            pstmt.setInt(3, userId); 
            pstmt.setInt(4, userId); 
            pstmt.setInt(5, userId); 

            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    PrivateMessage msg = new PrivateMessage();
                    // 1. 提取基础实体信息
                    msg.setId(rs.getInt("id"));
                    msg.setSenderId(rs.getInt("sender_id"));
                    msg.setReceiverId(rs.getInt("receiver_id"));
                    msg.setContent(rs.getString("content"));
                    msg.setCreateTime(rs.getTimestamp("create_time"));
                    msg.setIsRead(rs.getInt("is_read"));
                    
                    // 2. 注入关联的对方姓名和头像供前端渲染会话卡片
                    msg.setTargetName(rs.getString("target_name"));
                    msg.setTargetAvatar(rs.getString("target_avatar"));
                    
                    // 3. 【✅ 核心新增】提取数据库刚刚算好的真实未读条数
                    msg.setUnreadCount(rs.getInt("unread_count"));
                    
                    list.add(msg);
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }
        return list;
    }

    /**
     * 发送私信 (Create - 接收实体参数版)
     */
    public boolean sendMessage(PrivateMessage msg) {
        return sendMessage(msg.getSenderId(), msg.getReceiverId(), msg.getContent());
    }

    /**
     * 发送私信 (Create - 基础参数重载版)
     */
    public boolean sendMessage(int senderId, int receiverId, String content) {
        String sql = "INSERT INTO sys_private_message (sender_id, receiver_id, content, is_read, create_time) VALUES (?, ?, ?, 0, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, senderId);
            pstmt.setInt(2, receiverId);
            pstmt.setString(3, content);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * 获取两个用户之间的聊天记录 (Read - 时间正序排列)
     * 同时关联查询发送者的头像和姓名，方便前端直接渲染。
     */
    public List<PrivateMessage> getChatHistory(int userId1, int userId2) {
        List<PrivateMessage> list = new ArrayList<>();
        String sql = "SELECT m.*, u.real_name AS sender_name, u.avatar AS sender_avatar " +
                     "FROM sys_private_message m " +
                     "JOIN sys_user u ON m.sender_id = u.id " +
                     "WHERE (m.sender_id = ? AND m.receiver_id = ?) " +
                     "   OR (m.sender_id = ? AND m.receiver_id = ?) " +
                     "ORDER BY m.create_time ASC";
                     
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId1);
            pstmt.setInt(2, userId2);
            pstmt.setInt(3, userId2);
            pstmt.setInt(4, userId1);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    PrivateMessage pm = new PrivateMessage();
                    pm.setId(rs.getInt("id"));
                    pm.setSenderId(rs.getInt("sender_id"));
                    pm.setReceiverId(rs.getInt("receiver_id"));
                    pm.setContent(rs.getString("content"));
                    pm.setIsRead(rs.getInt("is_read"));
                    pm.setCreateTime(rs.getTimestamp("create_time"));
                    
                    // 扩展字段
                    pm.setSenderName(rs.getString("sender_name"));
                    pm.setSenderAvatar(rs.getString("sender_avatar"));
                    list.add(pm);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    /**
     * 将某个发送者发给当前接收者的所有未读消息标记为已读 (Update)
     */
    public boolean markAsRead(int senderId, int receiverId) {
        String sql = "UPDATE sys_private_message SET is_read = 1 WHERE sender_id = ? AND receiver_id = ? AND is_read = 0";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, senderId);
            pstmt.setInt(2, receiverId);
            pstmt.executeUpdate();
            return true;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * 清空双方的对话记录 (Delete)
     */
    public boolean clearConversation(int userId1, int userId2) {
        String sql = "DELETE FROM sys_private_message WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId1); pstmt.setInt(2, userId2);
            pstmt.setInt(3, userId2); pstmt.setInt(4, userId1);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) { 
            e.printStackTrace(); 
            return false; 
        }
    }
    
    /**
     * 获取当前用户的未读私信总数 (Read - 用于前端红点提示)
     */
    public int getUnreadCount(int currentUserId) {
        String sql = "SELECT COUNT(*) FROM sys_private_message WHERE receiver_id = ? AND is_read = 0";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, currentUserId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt(1);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return 0;
    }
}