package com.contacts.dao;

import com.contacts.entity.Announcement;
import com.contacts.entity.AnnouncementReply;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.ArrayList;
import java.util.List;

public class AnnouncementDao {

    public boolean addAnnouncement(Announcement announcement) {
        String sql = "INSERT INTO sys_announcement (admin_id, title, content, category, is_top, expire_time, create_time) VALUES (?, ?, ?, ?, ?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, announcement.getAdminId());
            pstmt.setString(2, announcement.getTitle());
            pstmt.setString(3, announcement.getContent());
            pstmt.setString(4, announcement.getCategory());
            pstmt.setInt(5, announcement.getIsTop());
            if (announcement.getExpireTime() != null) {
                pstmt.setTimestamp(6, new java.sql.Timestamp(announcement.getExpireTime().getTime()));
            } else {
                pstmt.setNull(6, Types.TIMESTAMP);
            }
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean updateAnnouncement(Announcement announcement) {
        String sql = "UPDATE sys_announcement SET title = ?, content = ?, category = ?, is_top = ?, expire_time = ? WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, announcement.getTitle());
            pstmt.setString(2, announcement.getContent());
            pstmt.setString(3, announcement.getCategory());
            pstmt.setInt(4, announcement.getIsTop());
            if (announcement.getExpireTime() != null) {
                pstmt.setTimestamp(5, new java.sql.Timestamp(announcement.getExpireTime().getTime()));
            } else {
                pstmt.setNull(5, Types.TIMESTAMP);
            }
            pstmt.setInt(6, announcement.getId());
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean deleteAnnouncement(int id) {
        String sql = "DELETE FROM sys_announcement WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public com.contacts.entity.Announcement getAnnouncementById(int id) {
        com.contacts.entity.Announcement announcement = null;
        // 【核心加固】改用 LEFT JOIN，防止由于发布人账号数据变动导致整条公告查不出来的致命 500 错误
        String sql = "SELECT a.*, u.real_name AS admin_name FROM sys_announcement a LEFT JOIN sys_user u ON a.admin_id = u.id WHERE a.id = ?";
        try (java.sql.Connection conn = com.contacts.utils.DBUtil.getConnection();
             java.sql.PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (java.sql.ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    announcement = extractFromResultSet(rs);
                }
            }
        } catch (java.sql.SQLException e) {
            e.printStackTrace();
        }
        return announcement;
    }

    public List<Announcement> getValidAnnouncements() {
        List<Announcement> list = new ArrayList<>();
        String sql = "SELECT a.*, u.real_name AS admin_name FROM sys_announcement a JOIN sys_user u ON a.admin_id = u.id " +
                     "WHERE a.expire_time IS NULL OR a.expire_time > NOW() ORDER BY a.is_top DESC, a.create_time DESC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                list.add(extractFromResultSet(rs));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public List<Announcement> getAllAnnouncements() {
        List<Announcement> list = new ArrayList<>();
        String sql = "SELECT a.*, u.real_name AS admin_name FROM sys_announcement a JOIN sys_user u ON a.admin_id = u.id ORDER BY a.create_time DESC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                list.add(extractFromResultSet(rs));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public List<Announcement> getTopAnnouncements() {
        List<Announcement> list = new ArrayList<>();
        String sql = "SELECT a.*, u.real_name AS admin_name FROM sys_announcement a JOIN sys_user u ON a.admin_id = u.id WHERE a.is_top = 1 ORDER BY a.create_time DESC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                list.add(extractFromResultSet(rs));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    private com.contacts.entity.Announcement extractFromResultSet(java.sql.ResultSet rs) throws java.sql.SQLException {
        com.contacts.entity.Announcement a = new com.contacts.entity.Announcement();
        a.setId(rs.getInt("id"));
        a.setAdminId(rs.getInt("admin_id"));
        a.setTitle(rs.getString("title"));
        a.setContent(rs.getString("content"));
        a.setCategory(rs.getString("category"));
        a.setIsTop(rs.getInt("is_top"));
        a.setExpireTime(rs.getTimestamp("expire_time"));
        a.setCreateTime(rs.getTimestamp("create_time"));
        
        // 【核心加固】补齐物理附件字段提取，防止详情页读取附件路径时发生断裂
        try {
            a.setAttachmentUrl(rs.getString("attachment_url"));
        } catch (java.sql.SQLException e) {
            // 容错处理
        }
        
        a.setAdminName(rs.getString("admin_name") == null ? "已注销管理员" : rs.getString("admin_name")); 
        return a;
    }
    
    // 1. 记录用户已读（利用 INSERT IGNORE 防止重复写入报错）
    public void markAsRead(int announcementId, int userId) {
        String sql = "INSERT IGNORE INTO sys_announcement_read (announcement_id, user_id, read_time) VALUES (?, ?, NOW())";
        try (java.sql.Connection conn = com.contacts.utils.DBUtil.getConnection();
             java.sql.PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, announcementId);
            pstmt.setInt(2, userId);
            pstmt.executeUpdate();
        } catch (java.sql.SQLException e) {
            e.printStackTrace();
        }
    }

    // 2. 获取某一公告的已读人数
    public int getReadCount(int announcementId) {
        String sql = "SELECT COUNT(*) FROM sys_announcement_read WHERE announcement_id = ?";
        try (java.sql.Connection conn = com.contacts.utils.DBUtil.getConnection();
             java.sql.PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, announcementId);
            try (java.sql.ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) return rs.getInt(1);
            }
        } catch (java.sql.SQLException e) {
            e.printStackTrace();
        }
        return 0;
    }

    // 3. 获取全班总有效人数
    public int getTotalUserCount() {
        String sql = "SELECT COUNT(*) FROM sys_user WHERE status = 1";
        try (java.sql.Connection conn = com.contacts.utils.DBUtil.getConnection();
             java.sql.PreparedStatement pstmt = conn.prepareStatement(sql);
             java.sql.ResultSet rs = pstmt.executeQuery()) {
            if (rs.next()) return rs.getInt(1);
        } catch (java.sql.SQLException e) {
            e.printStackTrace();
        }
        return 0;
    }

    // 4. 升级版发布公告（支持附件 URL 写入）
    public boolean addAnnouncementWithAttachment(com.contacts.entity.Announcement a) {
        String sql = "INSERT INTO sys_announcement (admin_id, title, content, category, is_top, expire_time, attachment_url, create_time) VALUES (?, ?, ?, ?, ?, ?, ?, NOW())";
        try (java.sql.Connection conn = com.contacts.utils.DBUtil.getConnection();
             java.sql.PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, a.getAdminId());
            pstmt.setString(2, a.getTitle());
            pstmt.setString(3, a.getContent());
            pstmt.setString(4, a.getCategory());
            pstmt.setInt(5, a.getIsTop());
            if (a.getExpireTime() != null) {
                pstmt.setTimestamp(6, new java.sql.Timestamp(a.getExpireTime().getTime()));
            } else {
                pstmt.setNull(6, java.sql.Types.TIMESTAMP);
            }
            if (a.getAttachmentUrl() != null) {
                pstmt.setString(7, a.getAttachmentUrl());
            } else {
                pstmt.setNull(7, java.sql.Types.VARCHAR);
            }
            return pstmt.executeUpdate() > 0;
        } catch (java.sql.SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
    
    // 获取某一作业公告的已提交人数
    public int getSubmittedCount(int announcementId) {
        String sql = "SELECT COUNT(DISTINCT user_id) FROM sys_announcement_reply WHERE announcement_id = ?";
        try (java.sql.Connection conn = com.contacts.utils.DBUtil.getConnection();
             java.sql.PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, announcementId);
            try (java.sql.ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) return rs.getInt(1);
            }
        } catch (java.sql.SQLException e) { e.printStackTrace(); }
        return 0;
    }

    /**
     * 1. 提交学生回执记录 (已升级容错机制)
     */
    public boolean addReply(int annId, int userId, String replyContent, String fileUrl) {
        // ✅ 核心修复：强制对齐表名 sys_announcement_reply
        String sql = "INSERT INTO sys_announcement_reply (announcement_id, user_id, reply_content, file_url, submit_time) VALUES (?, ?, ?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, annId);
            pstmt.setInt(2, userId);
            pstmt.setString(3, replyContent == null ? "" : replyContent);
            pstmt.setString(4, fileUrl);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            System.err.println("❌ addReply SQL 执行拦截！请检查 sys_announcement_reply 表是否已建好：");
            e.printStackTrace();
            return false;
        }
    }

    /**
     * 2. 获取该公告的所有回执名单及对应学生的详情 (已升级关联查询)
     */
    public List<AnnouncementReply> getRepliesByAnnouncementId(int annId) {
        List<AnnouncementReply> list = new ArrayList<>();
        // ✅ 核心修复：联合查询 sys_user 获取学生的姓名和头像
        String sql = "SELECT r.*, u.real_name AS user_name, u.student_no, u.avatar AS user_avatar " +
                     "FROM sys_announcement_reply r " +
                     "JOIN sys_user u ON r.user_id = u.id " +
                     "WHERE r.announcement_id = ? " +
                     "ORDER BY r.submit_time DESC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, annId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    AnnouncementReply rep = new AnnouncementReply();
                    rep.setId(rs.getInt("id"));
                    rep.setAnnouncementId(rs.getInt("announcement_id"));
                    rep.setUserId(rs.getInt("user_id"));
                    rep.setReplyContent(rs.getString("reply_content"));
                    rep.setFileUrl(rs.getString("file_url"));
                    rep.setSubmitTime(rs.getTimestamp("submit_time"));
                    
                    // 填入从 sys_user 表 JOIN 出来的学生资料
                    rep.setUserName(rs.getString("user_name"));
                    rep.setStudentNo(rs.getString("student_no"));
                    rep.setUserAvatar(rs.getString("user_avatar"));
                    list.add(rep);
                }
            }
        } catch (SQLException e) {
            System.err.println("❌ getRepliesByAnnouncementId 异常！");
            e.printStackTrace();
        }
        return list;
    }
}