package com.contacts.dao;

import com.contacts.entity.Friendship;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * sys_friendship 表的数据访问层（采用严格状态机处理逻辑与双向对等校验）
 */
public class FriendshipDao {

    /**
     * 发起好友申请（或反向自动建立好友）- 核心状态机实现
     * @param userId 发起人ID
     * @param friendId 接收人ID
     */
    public boolean sendRequest(int userId, int friendId) {
        // 1. 检查对方是否已经对“我”发起过好友申请
        String checkReverseSql = "SELECT id, status FROM sys_friendship WHERE user_id = ? AND friend_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(checkReverseSql)) {
            pstmt.setInt(1, friendId);
            pstmt.setInt(2, userId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    int status = rs.getInt("status");
                    if (status == 0) {
                        // 对方已申请加我，现在我点加他，直接自动互认为好友(更新为 status = 1)
                        return acceptRequest(userId, friendId);
                    } else if (status == 1) {
                        return true; // 已经是好友了，无需重复操作
                    }
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }

        // 2. 检查自己是否之前已经发过申请，防止重复 INSERT 报错
        String checkSelfSql = "SELECT id FROM sys_friendship WHERE user_id = ? AND friend_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(checkSelfSql)) {
            pstmt.setInt(1, userId);
            pstmt.setInt(2, friendId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return true; // 已经发过申请了，直接返回成功提示
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }

        // 3. 正常插入一条等待验证的申请 (status = 0)
        String insertSql = "INSERT INTO sys_friendship (user_id, friend_id, status, create_time) VALUES (?, ?, 0, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(insertSql)) {
            pstmt.setInt(1, userId);
            pstmt.setInt(2, friendId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * 同意好友申请 - 确保双向好友映射闭环
     * @param currentUserId 当前操作同意的用户ID（接收方）
     * @param senderId 申请发起人ID
     */
    public boolean acceptRequest(int currentUserId, int senderId) {
        // 将原申请状态改为 1
        String updateSql = "UPDATE sys_friendship SET status = 1 WHERE user_id = ? AND friend_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(updateSql)) {
            pstmt.setInt(1, senderId);
            pstmt.setInt(2, currentUserId);
            int rows = pstmt.executeUpdate();
            
            // 为了保证双向查询和社交逻辑绝对对称，主动插入一条反向的互为好友映射
            if (rows > 0) {
                ensureBidirectionalMapping(currentUserId, senderId);
                return true;
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }
        return false;
    }

    /**
     * 私有辅助：建立双向关系映射，使用 INSERT IGNORE 优雅避免唯一索引冲突
     */
    private void ensureBidirectionalMapping(int u1, int u2) {
        String sql = "INSERT IGNORE INTO sys_friendship (user_id, friend_id, status, create_time) VALUES (?, ?, 1, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, u1);
            pstmt.setInt(2, u2);
            pstmt.executeUpdate();
        } catch (SQLException e) { 
            /* 忽略重复插入异常 */ 
        }
    }

    /**
     * 向下兼容方法：发送好友申请 (Create)
     * 内部转调增强后的 sendRequest 方法，防止旧项目里的 Service 层报错
     */
    public boolean addFriendRequest(int userId, int friendId) {
        return sendRequest(userId, friendId);
    }

    /**
     * 更新好友状态 (Update - 同意或拒绝)
     * @param userId 发起人ID
     * @param friendId 接收人ID (或者当前用户ID)
     * @param status 1:已同意, 2:已拒绝
     */
    public boolean updateFriendStatus(int userId, int friendId, int status) {
        if (status == 1) {
            // 如果是同意操作，走全新封装的双向闭环逻辑
            return acceptRequest(friendId, userId);
        }
        
        // 如果是拒绝或其他自定义状态，常规更新
        String sql = "UPDATE sys_friendship SET status = ? WHERE user_id = ? AND friend_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, status);
            pstmt.setInt(2, userId);
            pstmt.setInt(3, friendId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * 【步骤 (1) 核心重构】判断是否为正式好友 (状态必须为 1)
     * 采用双向对等统计校验 SQL，确保无死锁、无漏查
     */
    public boolean isFriend(int userId1, int userId2) {
        String sql = "SELECT COUNT(*) FROM sys_friendship WHERE " +
                     "((user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)) " +
                     "AND status = 1";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // 严格按顺序注入传参: userId1, userId2, userId2, userId1
            pstmt.setInt(1, userId1); 
            pstmt.setInt(2, userId2);
            pstmt.setInt(3, userId2); 
            pstmt.setInt(4, userId1);
            try (ResultSet rs = pstmt.executeQuery()) { 
                if (rs.next()) {
                    return rs.getInt(1) > 0;
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }
        return false;
    }

    /**
     * 【新增底盘支持】双向检查：两者之间是否存在待审批的申请 (status = 0)
     * 直接供 FriendshipService 调用，避免在 Java 内存里做耗时的 List 循环遍历
     */
    public boolean hasPendingRequest(int userId1, int userId2) {
        String sql = "SELECT COUNT(*) FROM sys_friendship WHERE " +
                     "((user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)) " +
                     "AND status = 0";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId1); 
            pstmt.setInt(2, userId2);
            pstmt.setInt(3, userId2); 
            pstmt.setInt(4, userId1);
            try (ResultSet rs = pstmt.executeQuery()) { 
                if (rs.next()) {
                    return rs.getInt(1) > 0;
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }
        return false;
    }

    /**
     * 【新增底盘支持】双向检查：两用户之间是否在数据库中已有映射记录（无论 status 是多少）
     */
    public boolean recordExists(int userId1, int userId2) {
        String sql = "SELECT COUNT(*) FROM sys_friendship WHERE " +
                     "(user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId1); 
            pstmt.setInt(2, userId2);
            pstmt.setInt(3, userId2); 
            pstmt.setInt(4, userId1);
            try (ResultSet rs = pstmt.executeQuery()) { 
                if (rs.next()) {
                    return rs.getInt(1) > 0;
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }
        return false;
    }

    /**
     * 获取指定用户的已通过好友列表 (Read)
     * 【终极修复】使用 UNION 和 IN 子查询完美避开 MySQL 8.0 ONLY_FULL_GROUP_BY 严格模式报错，绝对去重！
     */
    public List<Friendship> getFriendList(int currentUserId) {
        List<Friendship> list = new ArrayList<>();
        
        // 核心突破：直接从 sys_user 表查询，条件是该用户的 ID 在“我加的人”或“加我的人”的通过名单中
        String sql = "SELECT u.id AS target_user_id, u.real_name AS friend_name, u.avatar AS friend_avatar, u.bio AS friend_bio " +
                     "FROM sys_user u " +
                     "WHERE u.id IN (" +
                     "    SELECT friend_id FROM sys_friendship WHERE user_id = ? AND status = 1 " +
                     "    UNION " +
                     "    SELECT user_id FROM sys_friendship WHERE friend_id = ? AND status = 1" +
                     ")";
                     
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // 给两个 UNION 子查询分别注入当前登录人 ID
            pstmt.setInt(1, currentUserId);
            pstmt.setInt(2, currentUserId);
            
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    Friendship f = new Friendship();
                    // 这里我们把目标聊天对象的 ID 存入 FriendId 字段中，供 JSP 渲染发起私聊的参数
                    f.setFriendId(rs.getInt("target_user_id")); 
                    f.setFriendName(rs.getString("friend_name"));
                    f.setFriendAvatar(rs.getString("friend_avatar"));
                    f.setFriendBio(rs.getString("friend_bio"));
                    list.add(f);
                }
            }
        } catch (SQLException e) {
            System.err.println("❌ 获取好友列表 SQL 执行异常：");
            e.printStackTrace();
        }
        return list;
    }

    /**
     * 获取别人发给“我”的、尚在等待验证的好友申请 (Read)
     */
    public List<Friendship> getPendingRequests(int userId) {
        List<Friendship> list = new ArrayList<>();
        String sql = "SELECT f.*, u.real_name AS friend_name, u.avatar AS friend_avatar " +
                     "FROM sys_friendship f " +
                     "JOIN sys_user u ON f.user_id = u.id " +
                     "WHERE f.friend_id = ? AND f.status = 0";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    Friendship f = new Friendship();
                    f.setId(rs.getInt("id")); 
                    f.setUserId(rs.getInt("user_id")); 
                    f.setFriendId(rs.getInt("friend_id"));
                    f.setStatus(rs.getInt("status"));
                    f.setCreateTime(rs.getDate("create_time"));
                    
                    f.setFriendName(rs.getString("friend_name")); 
                    f.setFriendAvatar(rs.getString("friend_avatar"));
                    list.add(f);
                }
            }
        } catch (SQLException e) { 
            e.printStackTrace(); 
        }
        return list;
    }

    /**
     * 删除好友关系 (Delete) - 彻底清除双向关联或单向申请
     */
    public boolean deleteFriend(int userId, int friendId) {
        String sql = "DELETE FROM sys_friendship WHERE (user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            pstmt.setInt(2, friendId);
            pstmt.setInt(3, friendId);
            pstmt.setInt(4, userId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * 【新增方法】单向检查：senderId 是否向 receiverId 发送过待审批的好友申请 (status = 0)
     */
    public boolean hasSentRequest(int senderId, int receiverId) {
        String sql = "SELECT COUNT(*) FROM sys_friendship WHERE user_id = ? AND friend_id = ? AND status = 0";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, senderId);
            pstmt.setInt(2, receiverId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt(1) > 0;
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }
}