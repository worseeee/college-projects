package com.contacts.dao;

import com.contacts.entity.Homework;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.ArrayList;
import java.util.List;

public class HomeworkDao {

    public boolean addHomework(Homework homework) {
        String sql = "INSERT INTO sys_homework (admin_id, title, content, attachment_url, deadline, create_time) VALUES (?, ?, ?, ?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, homework.getAdminId());
            pstmt.setString(2, homework.getTitle());
            pstmt.setString(3, homework.getContent());
            if (homework.getAttachmentUrl() != null) {
                pstmt.setString(4, homework.getAttachmentUrl());
            } else {
                pstmt.setNull(4, Types.VARCHAR);
            }
            pstmt.setTimestamp(5, new java.sql.Timestamp(homework.getDeadline().getTime()));
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean updateHomework(Homework homework) {
        String sql = "UPDATE sys_homework SET title = ?, content = ?, attachment_url = ?, deadline = ? WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, homework.getTitle());
            pstmt.setString(2, homework.getContent());
            if (homework.getAttachmentUrl() != null) {
                pstmt.setString(3, homework.getAttachmentUrl());
            } else {
                pstmt.setNull(3, Types.VARCHAR);
            }
            pstmt.setTimestamp(4, new java.sql.Timestamp(homework.getDeadline().getTime()));
            pstmt.setInt(5, homework.getId());
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean deleteHomework(int id) {
        String sql = "DELETE FROM sys_homework WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public Homework getHomeworkById(int id) {
        Homework homework = null;
        String sql = "SELECT h.*, u.real_name AS admin_name FROM sys_homework h JOIN sys_user u ON h.admin_id = u.id WHERE h.id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    homework = extractFromResultSet(rs);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return homework;
    }

    public List<Homework> getHomeworkList() {
        List<Homework> list = new ArrayList<>();
        String sql = "SELECT h.*, u.real_name AS admin_name FROM sys_homework h JOIN sys_user u ON h.admin_id = u.id ORDER BY h.deadline ASC";
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

    private Homework extractFromResultSet(ResultSet rs) throws SQLException {
        Homework h = new Homework();
        h.setId(rs.getInt("id"));
        h.setAdminId(rs.getInt("admin_id"));
        h.setTitle(rs.getString("title"));
        h.setContent(rs.getString("content"));
        h.setAttachmentUrl(rs.getString("attachment_url"));
        h.setDeadline(rs.getTimestamp("deadline"));
        h.setCreateTime(rs.getTimestamp("create_time"));
        // 如果 Entity 增加了 adminName 扩展字段
        // h.setAdminName(rs.getString("admin_name")); 
        return h;
    }
}