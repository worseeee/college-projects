package com.contacts.service;

import com.contacts.dao.LogDao;
import com.contacts.dao.UserDao;
import com.contacts.entity.User;
import com.contacts.utils.MD5Util;

import java.util.List;

public class UserService {
    
    private UserDao userDao = new UserDao();
    private LogDao logDao = new LogDao();

    public User login(String username, String password, String ipAddress) {
        if (username == null || password == null) return null;
        String encryptedPassword = MD5Util.encrypt(password);
        User user = userDao.login(username, encryptedPassword);
        
        if (user != null) {
            if (user.getStatus() == 1 || user.getStatus() == 2) {
                logDao.addLog(user.getId(), "用户登录成功", ipAddress);
            }
        } else {
            logDao.addLog(null, "尝试登录失败: " + username, ipAddress);
        }
        return user;
    }

    public void logout(int userId, String ipAddress) {
        logDao.addLog(userId, "用户安全退出", ipAddress);
    }

    public boolean register(User user, String ipAddress) {
        user.setPassword(MD5Util.encrypt(user.getPassword()));
        boolean success = userDao.register(user);
        if (success) {
            logDao.addLog(null, "新用户注册申请: " + user.getStudentNo(), ipAddress);
        }
        return success;
    }

    public boolean updateProfile(User user, String ipAddress) {
        User existUser = userDao.getUserById(user.getId());
        if (existUser == null) return false;
        
        boolean success = userDao.updateUser(user);
        if (success) {
            logDao.addLog(user.getId(), "更新了个人资料", ipAddress);
        }
        return success;
    }

    public boolean changePassword(int userId, String oldPassword, String newPassword, String ipAddress) {
        User user = userDao.getUserById(userId);
        if (user == null) return false;
        
        if (!user.getPassword().equals(MD5Util.encrypt(oldPassword))) {
            return false; // 旧密码错误
        }
        
        boolean success = userDao.updatePassword(userId, MD5Util.encrypt(newPassword));
        if (success) {
            logDao.addLog(userId, "修改了登录密码", ipAddress);
        }
        return success;
    }

    public User getUserById(int id) {
        return userDao.getUserById(id);
    }

    public List<User> getContactsList(int currentUserId) {
        return userDao.getContactsList(currentUserId);
    }

    public List<User> searchUsers(String keyword, int currentUserId) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return getContactsList(currentUserId);
        }
        return userDao.searchUsers(keyword, currentUserId);
    }

    public boolean updatePrivacySettings(int userId, int phonePrivacy, int wechatPrivacy, int qqPrivacy, String ipAddress) {
        User user = userDao.getUserById(userId);
        if (user == null) return false;
        user.setPrivacyPhone(phonePrivacy);
        user.setPrivacyWechat(wechatPrivacy);
        user.setPrivacyQq(qqPrivacy);
        boolean success = userDao.updateUser(user);
        if (success) {
            logDao.addLog(userId, "更新了隐私设置", ipAddress);
        }
        return success;
    }

    public boolean uploadAvatar(int userId, String avatarPath, String ipAddress) {
        User user = userDao.getUserById(userId);
        if (user == null) return false;
        user.setAvatar(avatarPath);
        boolean success = userDao.updateUser(user);
        if (success) {
            logDao.addLog(userId, "更新了个人头像", ipAddress);
        }
        return success;
    }
    
    public java.util.List<com.contacts.entity.User> getPendingUsers(int role) {
        if (role != 2) return null; // 仅管理员有权查看
        return userDao.getPendingUsers();
    }

    public boolean auditUser(int targetUserId, int actionStatus, int adminId, int role, String ipAddress) {
        if (role != 2) return false; // 越权拦截
        boolean success = userDao.updateUserStatus(targetUserId, actionStatus);
        if (success) {
            String actionName = actionStatus == 1 ? "通过" : "拒绝";
            logDao.addLog(adminId, actionName + "了新生注册(用户ID:" + targetUserId + ")", ipAddress);
        }
        return success;
    }
}