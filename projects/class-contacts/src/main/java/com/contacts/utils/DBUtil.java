package com.contacts.utils;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * @title 现代高可用数据库连接中心
 * @description 规范化驱动加载，提供彻底免于资源泄露的底层保护
 */
public class DBUtil {
    private static final String URL = "jdbc:mysql://localhost:3306/class_contacts_db?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true&useUnicode=true&characterEncoding=UTF-8";
    private static final String USER = "root";
    private static final String PASSWORD = System.getenv().getOrDefault("CONTACTS_DB_PASSWORD", ""); // 请在此处配置你真实的 MySQL 密码

    static {
        try {
            // 显式加载 MySQL 8.x 现代驱动，防范 Tomcat 容器上下文加载失败
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            System.err.println("❌ 严重致命：未能成功挂载 MySQL 驱动，请检查 WEB-INF/lib 目录下是否存在连接器 Jar 包！");
            e.printStackTrace();
        }
    }

    /**
     * 获取一个纯净的、线程独立的独占式连接通道
     */
    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }

    /**
     * @description 安全关闭工具，防御各种深层因 NPE 导致关闭失败而引发的服务器句柄泄露风险
     */
    public static void close(ResultSet rs, Statement stmt, Connection conn) {
        try {
            if (rs != null) rs.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        try {
            if (stmt != null) stmt.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        try {
            if (conn != null) conn.close();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}