package com.contacts.dao;

import com.contacts.entity.Activity;
import com.contacts.entity.User;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class ActivityDao {

    public boolean addActivity(Activity activity) {
        String sql = "INSERT INTO sys_activity (admin_id, title, content, activity_time, create_time) VALUES (?, ?, ?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, activity.getAdminId());
            pstmt.setString(2, activity.getTitle());
            pstmt.setString(3, activity.getContent());
            pstmt.setTimestamp(4, new java.sql.Timestamp(activity.getActivityTime().getTime()));
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean updateActivity(Activity activity) {
        String sql = "UPDATE sys_activity SET title = ?, content = ?, activity_time = ? WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, activity.getTitle());
            pstmt.setString(2, activity.getContent());
            pstmt.setTimestamp(3, new java.sql.Timestamp(activity.getActivityTime().getTime()));
            pstmt.setInt(4, activity.getId());
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean deleteActivity(int id) {
        String sql = "DELETE FROM sys_activity WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public Activity getActivityById(int id) {
        Activity activity = null;
        String sql = "SELECT a.*, u.real_name AS admin_name FROM sys_activity a JOIN sys_user u ON a.admin_id = u.id WHERE a.id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    activity = extractFromResultSet(rs);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return activity;
    }

    public List<Activity> getActivityListWithCount() {
        List<Activity> list = new ArrayList<>();
        String sql = "SELECT a.*, u.real_name AS admin_name, COUNT(e.id) AS enrolled_count " +
                     "FROM sys_activity a " +
                     "JOIN sys_user u ON a.admin_id = u.id " +
                     "LEFT JOIN sys_activity_enrollment e ON a.id = e.activity_id " +
                     "GROUP BY a.id ORDER BY a.create_time DESC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                Activity act = extractFromResultSet(rs);
                act.setEnrolledCount(rs.getInt("enrolled_count"));
                list.add(act);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public List<Activity> getAllActivities() {
        List<Activity> list = new ArrayList<>();
        String sql = "SELECT a.*, u.real_name AS admin_name FROM sys_activity a JOIN sys_user u ON a.admin_id = u.id ORDER BY a.create_time DESC";
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

    public boolean enrollActivity(int activityId, int userId) {
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

    public boolean cancelEnrollment(int activityId, int userId) {
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

    public List<User> getEnrollmentList(int activityId) {
        List<User> list = new ArrayList<>();
        String sql = "SELECT u.* FROM sys_user u JOIN sys_activity_enrollment e ON u.id = e.user_id WHERE e.activity_id = ? ORDER BY e.create_time ASC";
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

    private Activity extractFromResultSet(ResultSet rs) throws SQLException {
        Activity a = new Activity();
        a.setId(rs.getInt("id"));
        a.setAdminId(rs.getInt("admin_id"));
        a.setTitle(rs.getString("title"));
        a.setContent(rs.getString("content"));
        a.setActivityTime(rs.getTimestamp("activity_time"));
        a.setCreateTime(rs.getTimestamp("create_time"));
        a.setAdminName(rs.getString("admin_name")); // 扩展字段
        return a;
    }
}