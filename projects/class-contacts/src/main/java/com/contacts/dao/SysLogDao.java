package com.contacts.dao;

import com.contacts.entity.SysLog;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.ArrayList;
import java.util.List;

public class SysLogDao {

    public boolean addLog(SysLog log) {
        String sql = "INSERT INTO sys_log (user_id, action, ip_address, create_time) VALUES (?, ?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            if (log.getUserId() != null) {
                pstmt.setInt(1, log.getUserId());
            } else {
                pstmt.setNull(1, Types.INTEGER); // 未登录拦截操作
            }
            pstmt.setString(2, log.getAction());
            pstmt.setString(3, log.getIpAddress());
            
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<SysLog> getLogList(int offset, int limit) {
        List<SysLog> list = new ArrayList<>();
        String sql = "SELECT l.*, u.real_name AS operator_name FROM sys_log l LEFT JOIN sys_user u ON l.user_id = u.id ORDER BY l.create_time DESC LIMIT ?, ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, offset);
            pstmt.setInt(2, limit);
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

    public List<SysLog> getLogByUser(int userId) {
        List<SysLog> list = new ArrayList<>();
        String sql = "SELECT l.*, u.real_name AS operator_name FROM sys_log l JOIN sys_user u ON l.user_id = u.id WHERE l.user_id = ? ORDER BY l.create_time DESC";
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

    public boolean deleteOldLogs(int daysBefore) {
        String sql = "DELETE FROM sys_log WHERE create_time < DATE_SUB(NOW(), INTERVAL ? DAY)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, daysBefore);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    private SysLog extractFromResultSet(ResultSet rs) throws SQLException {
        SysLog l = new SysLog();
        l.setId(rs.getInt("id"));
        l.setUserId(rs.getInt("user_id"));
        l.setAction(rs.getString("action"));
        l.setIpAddress(rs.getString("ip_address"));
        l.setCreateTime(rs.getTimestamp("create_time"));
        l.setOperatorName(rs.getString("operator_name")); // 扩展字段
        return l;
    }
}