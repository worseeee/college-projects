package com.contacts.dao;

import com.contacts.entity.PhotoAlbum;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.ArrayList;
import java.util.List;

public class PhotoAlbumDao {

    public boolean addPhoto(PhotoAlbum photo) {
        // 严格遵守 SQL: id, user_id, photo_url, description, create_time
        String sql = "INSERT INTO sys_photo_album (user_id, photo_url, description, create_time) VALUES (?, ?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, photo.getUserId());
            pstmt.setString(2, photo.getPhotoUrl());
            if (photo.getDescription() != null) {
                pstmt.setString(3, photo.getDescription());
            } else {
                pstmt.setNull(3, Types.VARCHAR);
            }
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean deletePhoto(int id) {
        String sql = "DELETE FROM sys_photo_album WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public PhotoAlbum getPhotoById(int id) {
        PhotoAlbum photo = null;
        String sql = "SELECT p.*, u.real_name AS uploader_name FROM sys_photo_album p JOIN sys_user u ON p.user_id = u.id WHERE p.id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    photo = extractFromResultSet(rs);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return photo;
    }

    public List<PhotoAlbum> getPhotoList() {
        List<PhotoAlbum> list = new ArrayList<>();
        String sql = "SELECT p.*, u.real_name AS uploader_name FROM sys_photo_album p JOIN sys_user u ON p.user_id = u.id ORDER BY p.create_time DESC";
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

    public List<PhotoAlbum> getPhotoListByUser(int userId) {
        List<PhotoAlbum> list = new ArrayList<>();
        String sql = "SELECT p.*, u.real_name AS uploader_name FROM sys_photo_album p JOIN sys_user u ON p.user_id = u.id WHERE p.user_id = ? ORDER BY p.create_time DESC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, userId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    list.add(extractFromResultSet(rs));
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    private PhotoAlbum extractFromResultSet(ResultSet rs) throws SQLException {
        PhotoAlbum p = new PhotoAlbum();
        p.setId(rs.getInt("id"));
        p.setUserId(rs.getInt("user_id"));
        p.setPhotoUrl(rs.getString("photo_url"));
        p.setDescription(rs.getString("description"));
        p.setCreateTime(rs.getTimestamp("create_time"));
        p.setUploaderName(rs.getString("uploader_name")); // 要求中提到的扩展字段
        return p;
    }
}