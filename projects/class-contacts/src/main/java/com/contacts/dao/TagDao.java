package com.contacts.dao;

import com.contacts.entity.Tag;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class TagDao {

    public boolean addTag(String tagName) {
        String sql = "INSERT INTO sys_tag (name) VALUES (?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, tagName);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean deleteTag(int id) {
        String sql = "DELETE FROM sys_tag WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<Tag> getAllTags() {
        List<Tag> list = new ArrayList<>();
        String sql = "SELECT * FROM sys_tag ORDER BY id ASC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                Tag tag = new Tag();
                tag.setId(rs.getInt("id"));
                tag.setName(rs.getString("name"));
                list.add(tag);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public List<Tag> getTagsByUserId(int userId) {
        List<Tag> list = new ArrayList<>();
        String sql = "SELECT t.* FROM sys_tag t JOIN sys_user_tag ut ON t.id = ut.tag_id WHERE ut.user_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    Tag tag = new Tag();
                    tag.setId(rs.getInt("id"));
                    tag.setName(rs.getString("name"));
                    list.add(tag);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public boolean bindUserTag(int userId, int tagId) {
        String sql = "INSERT INTO sys_user_tag (user_id, tag_id) VALUES (?, ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            pstmt.setInt(2, tagId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false; // 重复绑定将抛出主键冲突异常并返回false
        }
    }

    public boolean removeUserTag(int userId, int tagId) {
        String sql = "DELETE FROM sys_user_tag WHERE user_id = ? AND tag_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            pstmt.setInt(2, tagId);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
}