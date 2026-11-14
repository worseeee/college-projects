package com.contacts.service;

import com.contacts.dao.HomeworkDao;
import com.contacts.dao.LogDao;
import com.contacts.entity.Homework;

import java.util.List;

/**
 * 作业管理模块业务逻辑层
 */
public class HomeworkService {

    private HomeworkDao homeworkDao = new HomeworkDao();
    private LogDao logDao = new LogDao();

    /**
     * 【核心修复】获取全部作业列表 - 专门解决 HomeworkServlet 第 39 行的报错
     */
    public List<Homework> getAllHomeworks() {
        return homeworkDao.getHomeworkList();
    }

    /**
     * 向下兼容：获取作业列表（与 DAO 层命名保持完全一致的同名重载）
     */
    public List<Homework> getHomeworkList() {
        return homeworkDao.getHomeworkList();
    }

    /**
     * 布置新作业（带安全操作日志审计）
     * @param hw 作业实体类
     * @param ipAddress 发起操作的客户端 IP
     * @return 是否发布成功
     */
    public boolean addHomework(Homework hw, String ipAddress) {
        if (hw == null || hw.getTitle() == null || hw.getTitle().trim().isEmpty()) {
            return false;
        }
        
        boolean success = homeworkDao.addHomework(hw);
        if (success && logDao != null && ipAddress != null) {
            logDao.addLog(hw.getTeacherId(), "布置了新作业: 《" + hw.getTitle() + "》", ipAddress);
        }
        return success;
    }

    /**
     * 基础重载：布置新作业（不带日志）
     */
    public boolean addHomework(Homework hw) {
        return homeworkDao.addHomework(hw);
    }

    /**
     * 删除作业（带安全操作日志审计）
     * @param id 作业ID
     * @param operatorId 执行删除操作的教师/管理员ID
     * @param ipAddress 发起操作的客户端 IP
     */
    public boolean deleteHomework(int id, Integer operatorId, String ipAddress) {
        boolean success = homeworkDao.deleteHomework(id);
        if (success && logDao != null && ipAddress != null && operatorId != null) {
            logDao.addLog(operatorId, "删除了作业ID: " + id, ipAddress);
        }
        return success;
    }

    /**
     * 基础重载：删除作业
     */
    public boolean deleteHomework(int id) {
        return homeworkDao.deleteHomework(id);
    }
}