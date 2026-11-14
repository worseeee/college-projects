package com.contacts.service;

import com.contacts.dao.LogDao;
import com.contacts.dao.SensitiveWordDao;

import java.util.List;

public class SensitiveWordService {

    private SensitiveWordDao sensitiveWordDao = new SensitiveWordDao();
    private LogDao logDao = new LogDao();

    public boolean addWord(String word, int adminId, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = sensitiveWordDao.addWord(word);
        if (success) logDao.addLog(adminId, "添加了敏感词汇", ipAddress);
        return success;
    }

    public boolean deleteWord(int id, int adminId, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = sensitiveWordDao.deleteWord(id);
        if (success) logDao.addLog(adminId, "移除了敏感词汇ID: " + id, ipAddress);
        return success;
    }

    public List<String> getAllWords() {
        return sensitiveWordDao.getAllWords();
    }

    public boolean containsSensitiveWord(String text) {
        return sensitiveWordDao.containsSensitiveWord(text);
    }
}