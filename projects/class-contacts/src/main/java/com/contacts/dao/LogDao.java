package com.contacts.dao;

import com.contacts.entity.SysLog;
import com.contacts.utils.DBUtil;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

/**
 * sys_log 表的数据访问层
 */
public class LogDao {

    /**
     * 写入系统日志 (Create)
     * * @param userId 操作者ID (若未登录拦截，则传入 null)
     * @param action 操作动作描述 (如 "尝试越权访问相册", "发布违规留言并被拦截")
     * @param ipAddress 客户端的真实IP地址
     */
    public void addLog(Integer userId, String action, String ipAddress) {
        String sql = "INSERT INTO sys_log (user_id, action, ip_address, create_time) VALUES (?, ?, ?, NOW())";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            // 处理 userId 为 null 的情况 (JDBC 处理 Null 有特定规范)
            if (userId != null) {
                pstmt.setInt(1, userId);
            } else {
                pstmt.setNull(1, java.sql.Types.INTEGER);
            }
            pstmt.setString(2, action);
            pstmt.setString(3, ipAddress);
            
            pstmt.executeUpdate();
            // 日志写入失败通常不影响主业务流程，故不抛出或返回严格校验
        } catch (SQLException e) {
            System.err.println("【严重警告】系统日志写入失败: " + e.getMessage());
        }
    }
}