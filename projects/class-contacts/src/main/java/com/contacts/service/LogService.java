package com.contacts.service;

import com.contacts.dao.LogDao;
import com.contacts.dao.SysLogDao;
import com.contacts.entity.SysLog;

import java.util.List;

public class LogService {

    private SysLogDao sysLogDao = new SysLogDao();
    private LogDao logDao = new LogDao(); // 旧版简单插入DAO，与SysLogDao合并逻辑

    public boolean addLog(SysLog log) {
        return sysLogDao.addLog(log);
    }

    public List<SysLog> getLogList(int offset, int limit, int role) {
        if (role != 2) return null; // 仅管理员可查看
        return sysLogDao.getLogList(offset, limit);
    }

    public List<SysLog> getLogByUser(int userId, int role) {
        if (role != 2) return null;
        return sysLogDao.getLogByUser(userId);
    }

    public boolean deleteOldLogs(int daysBefore, int adminId, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = sysLogDao.deleteOldLogs(daysBefore);
        if (success) logDao.addLog(adminId, "清理了 " + daysBefore + " 天前的系统日志", ipAddress);
        return success;
    }
}