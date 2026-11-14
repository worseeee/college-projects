package com.contacts.dao;

import com.contacts.entity.BoardMessage;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * sys_board_message 表的数据访问层
 */
public class BoardMessageDao {

    /**
     * 发布留言或回复 (Create)
     * @param parentId 0表示发布新帖，非0表示回复某条帖子
     */
    public boolean addMessage(int userId, String content, int parentId) {
        String sql = "INSERT INTO sys_board_message (user_id, content, parent_id, like_count, create_time) VALUES (?, ?, ?, 0, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            pstmt.setString(2, content);
            pstmt.setInt(3, parentId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * 分页获取主留言列表 (Read - 仅获取 parent_id = 0 的首层留言)
     * 关联查询发帖人的姓名和头像。
     * @param offset 偏移量
     * @param limit 每页条数
     */
    public List<BoardMessage> getMainMessages(int offset, int limit) {
        List<BoardMessage> list = new ArrayList<>();
        String sql = "SELECT b.*, u.real_name AS author_name, u.avatar AS author_avatar " +
                     "FROM sys_board_message b " +
                     "JOIN sys_user u ON b.user_id = u.id " +
                     "WHERE b.parent_id = 0 " +
                     "ORDER BY b.create_time DESC LIMIT ?, ?";
                     
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, offset);
            pstmt.setInt(2, limit);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    BoardMessage msg = extractMsgFromResultSet(rs);
                    list.add(msg);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    /**
     * 获取指定留言的所有回复 (Read)
     */
    public List<BoardMessage> getRepliesByParentId(int parentId) {
        List<BoardMessage> list = new ArrayList<>();
        String sql = "SELECT b.*, u.real_name AS author_name, u.avatar AS author_avatar " +
                     "FROM sys_board_message b " +
                     "JOIN sys_user u ON b.user_id = u.id " +
                     "WHERE b.parent_id = ? " +
                     "ORDER BY b.create_time ASC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, parentId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    list.add(extractMsgFromResultSet(rs));
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    /**
     * 删除留言 (Delete - 管理员或本人操作)
     * 注意：由于 MySQL 设置了外键，且本系统设计为父留言删除不会直接通过数据库级联删除子留言(避免自关联问题)，
     * 需要在 Service 层先调用删除子回复，再删父回复。
     */
    public boolean deleteMessage(int messageId) {
        String sql = "DELETE FROM sys_board_message WHERE id = ? OR parent_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, messageId);
            pstmt.setInt(2, messageId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * 留言点赞加一 (Update) - 企业级防重复点赞与防 NULL 陷阱版
     */
    public boolean incrementLike(int messageId, int userId) {
        // ✅ 修复点 1：表名对齐！强制使用 sys_board_like_record
        String insertRecordSql = "INSERT IGNORE INTO sys_board_like_record (message_id, user_id) VALUES (?, ?)";
        
        // ✅ 修复点 2：使用 IFNULL 兜底！防止数据库存在极端情况下的 NULL 导致 NULL + 1 = NULL
        String updateCountSql = "UPDATE sys_board_message SET like_count = IFNULL(like_count, 0) + 1 WHERE id = ?";
        
        Connection conn = null;
        PreparedStatement pstmt1 = null;
        PreparedStatement pstmt2 = null;
        try {
            conn = DBUtil.getConnection();
            conn.setAutoCommit(false); // 开启严格的数据库事务
            
            pstmt1 = conn.prepareStatement(insertRecordSql);
            pstmt1.setInt(1, messageId);
            pstmt1.setInt(2, userId);
            int rows = pstmt1.executeUpdate();
            
            if (rows > 0) {
                // 成功插入记录，说明是第一次点赞，继续让主表的点赞总数 +1
                pstmt2 = conn.prepareStatement(updateCountSql);
                pstmt2.setInt(1, messageId);
                pstmt2.executeUpdate();
                conn.commit(); // 提交事务
                return true;
            } else {
                // rows == 0，说明被 IGNORE 拦截，数据库已有记录，确认为重复点赞
                conn.rollback();
                return false;
            }
        } catch (SQLException e) {
            // ✅ 修复点 3：抛出红色高亮异常到控制台，拒绝静默死亡！
            System.err.println("❌ [严重错误] 点赞事务执行失败！请检查表名或字段是否存在！SQL异常信息：");
            e.printStackTrace();
            try { if (conn != null) conn.rollback(); } catch (SQLException ex) { ex.printStackTrace(); }
            return false;
        } finally {
            DBUtil.close(null, pstmt2, null);
            DBUtil.close(null, pstmt1, conn);
        }
    }
    
    /**
     * 获取单条留言详情（升级关联作者姓名与头像）
     */
    public BoardMessage getMessageById(int id) {
        BoardMessage msg = null;
        String sql = "SELECT b.*, u.real_name AS author_name, u.avatar AS author_avatar " +
                     "FROM sys_board_message b " +
                     "JOIN sys_user u ON b.user_id = u.id " +
                     "WHERE b.id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    msg = extractMsgFromResultSet(rs);
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }
        return msg;
    }
    
    private BoardMessage extractMsgFromResultSet(ResultSet rs) throws SQLException {
        BoardMessage msg = new BoardMessage();
        msg.setId(rs.getInt("id"));
        msg.setUserId(rs.getInt("user_id"));
        msg.setContent(rs.getString("content"));
        msg.setParentId(rs.getInt("parent_id"));
        msg.setLikeCount(rs.getInt("like_count"));
        msg.setCreateTime(rs.getDate("create_time"));
        msg.setAuthorName(rs.getString("author_name"));
        msg.setAuthorAvatar(rs.getString("author_avatar"));
        return msg;
    }
}