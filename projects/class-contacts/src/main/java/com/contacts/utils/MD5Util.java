package com.contacts.utils;

import java.security.MessageDigest;

/**
 * 密码加密工具类
 */
public class MD5Util {
    
    /**
     * 将明文密码转换为 32 位 MD5 密文
     */
    public static String encrypt(String source) {
        if (source == null || source.isEmpty()) {
            return null;
        }
        try {
            // 获取 MD5 摘要算法实例
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] bytes = md.digest(source.getBytes("UTF-8"));
            
            // 将字节数组转换为十六进制字符串
            StringBuilder sb = new StringBuilder();
            for (byte b : bytes) {
                String hex = Integer.toHexString(b & 0xFF);
                if (hex.length() == 1) {
                    sb.append("0"); // 补位
                }
                sb.append(hex);
            }
            return sb.toString();
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("MD5加密失败", e);
        }
    }
}