package com.contacts.dao;

import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class SensitiveWordDao {

    public boolean addWord(String word) {
        String sql = "INSERT INTO sys_sensitive_word (word) VALUES (?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, word);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean deleteWord(int id) {
        String sql = "DELETE FROM sys_sensitive_word WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<String> getAllWords() {
        List<String> list = new ArrayList<>();
        String sql = "SELECT word FROM sys_sensitive_word ORDER BY id ASC";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                list.add(rs.getString("word"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    /**
     * 高级技巧：利用 DB 层进行敏感词反向检索校验
     * @param text 待检测的文本 (如用户发表的留言)
     * @return true(包含违规词汇), false(安全通过)
     */
    public boolean containsSensitiveWord(String text) {
        if (text == null || text.trim().isEmpty()) {
            return false;
        }
        String sql = "SELECT 1 FROM sys_sensitive_word WHERE ? LIKE CONCAT('%', word, '%') LIMIT 1";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, text);
            try (ResultSet rs = pstmt.executeQuery()) {
                return rs.next(); // 若查询到结果，则证明 text 包含了库中的敏感词
            }
        } catch (SQLException e) {
            e.printStackTrace();
            // 为安全起见，若数据库异常，默认拦截
            return true; 
        }
    }
}