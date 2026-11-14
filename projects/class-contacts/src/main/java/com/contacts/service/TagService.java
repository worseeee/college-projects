package com.contacts.service;

import com.contacts.dao.LogDao;
import com.contacts.dao.TagDao;
import com.contacts.entity.Tag;

import java.util.List;

public class TagService {

    private TagDao tagDao = new TagDao();
    private LogDao logDao = new LogDao();

    public boolean addTag(String name, int adminId, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = tagDao.addTag(name);
        if (success) logDao.addLog(adminId, "添加了全局兴趣标签: " + name, ipAddress);
        return success;
    }

    public boolean deleteTag(int id, int adminId, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = tagDao.deleteTag(id);
        if (success) logDao.addLog(adminId, "删除了全局标签ID: " + id, ipAddress);
        return success;
    }

    public List<Tag> getAllTags() {
        return tagDao.getAllTags();
    }

    public boolean bindUserTag(int userId, int tagId, String ipAddress) {
        boolean success = tagDao.bindUserTag(userId, tagId);
        if (success) logDao.addLog(userId, "绑定了兴趣标签ID: " + tagId, ipAddress);
        return success;
    }

    public boolean removeUserTag(int userId, int tagId, String ipAddress) {
        boolean success = tagDao.removeUserTag(userId, tagId);
        if (success) logDao.addLog(userId, "移除了兴趣标签ID: " + tagId, ipAddress);
        return success;
    }

    public List<Tag> getTagsByUser(int userId) {
        return tagDao.getTagsByUserId(userId);
    }
}