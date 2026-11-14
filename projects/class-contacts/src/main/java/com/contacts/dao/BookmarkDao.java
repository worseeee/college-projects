package com.contacts.dao;

import com.contacts.utils.DBUtil;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class BookmarkDao {
    
    public boolean addBookmark(int userId, int targetId) {
        String sql = "INSERT IGNORE INTO user_bookmark (user_id, bookmarked_user_id) VALUES (?, ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            pstmt.setInt(2, targetId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    public boolean removeBookmark(int userId, int targetId) {
        String sql = "DELETE FROM user_bookmark WHERE user_id = ? AND bookmarked_user_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            pstmt.setInt(2, targetId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    public List<Integer> getBookmarkedUserIds(int userId) {
        List<Integer> list = new ArrayList<>();
        String sql = "SELECT bookmarked_user_id FROM user_bookmark WHERE user_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    list.add(rs.getInt("bookmarked_user_id"));
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }
}