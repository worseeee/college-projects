package com.contacts.dao;

import com.contacts.entity.ActivityEnrollment;
import com.contacts.entity.User;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class ActivityEnrollmentDao {

    public boolean enroll(int activityId, int userId) {
        String sql = "INSERT INTO sys_activity_enrollment (activity_id, user_id, create_time) VALUES (?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, activityId);
            pstmt.setInt(2, userId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean cancelEnroll(int activityId, int userId) {
        String sql = "DELETE FROM sys_activity_enrollment WHERE activity_id = ? AND user_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, activityId);
            pstmt.setInt(2, userId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<User> getEnrollUsers(int activityId) {
        List<User> list = new ArrayList<>();
        String sql = "SELECT u.id, u.real_name, u.student_no, u.avatar " +
                     "FROM sys_user u JOIN sys_activity_enrollment e ON u.id = e.user_id " +
                     "WHERE e.activity_id = ? ORDER BY e.create_time ASC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, activityId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    User user = new User();
                    user.setId(rs.getInt("id"));
                    user.setRealName(rs.getString("real_name"));
                    user.setStudentNo(rs.getString("student_no"));
                    user.setAvatar(rs.getString("avatar"));
                    list.add(user);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public int getEnrollCount(int activityId) {
        String sql = "SELECT COUNT(*) FROM sys_activity_enrollment WHERE activity_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, activityId);
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