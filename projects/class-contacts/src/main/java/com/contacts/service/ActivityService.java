package com.contacts.service;

import com.contacts.dao.ActivityDao;
import com.contacts.dao.ActivityEnrollmentDao;
import com.contacts.dao.LogDao;
import com.contacts.entity.Activity;
import com.contacts.entity.User;

import java.util.Date;
import java.util.List;

public class ActivityService {

    private ActivityDao activityDao = new ActivityDao();
    private ActivityEnrollmentDao enrollmentDao = new ActivityEnrollmentDao();
    private LogDao logDao = new LogDao();

    public boolean addActivity(Activity activity, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = activityDao.addActivity(activity);
        if (success) logDao.addLog(activity.getAdminId(), "发布了活动: " + activity.getTitle(), ipAddress);
        return success;
    }

    public boolean updateActivity(Activity activity, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = activityDao.updateActivity(activity);
        if (success) logDao.addLog(activity.getAdminId(), "更新了活动ID: " + activity.getId(), ipAddress);
        return success;
    }

    public boolean deleteActivity(int id, int adminId, int role, String ipAddress) {
        if (role != 2) return false;
        boolean success = activityDao.deleteActivity(id);
        if (success) logDao.addLog(adminId, "删除了活动ID: " + id, ipAddress);
        return success;
    }

    public Activity getActivityById(int id) {
        return activityDao.getActivityById(id);
    }

    public List<Activity> getActivityList() {
        return activityDao.getActivityListWithCount();
    }

    public int enrollActivity(int activityId, int userId, String ipAddress) {
        Activity activity = activityDao.getActivityById(activityId);
        if (activity == null) return -1; // 活动不存在
        
        // 业务规则：如果活动时间已经过去，则不能报名
        if (activity.getActivityTime().before(new Date())) {
            return -2; // 活动已过期
        }
        
        boolean success = enrollmentDao.enroll(activityId, userId); // 数据库层有联合主键防重复
        if (success) {
            logDao.addLog(userId, "报名了活动ID: " + activityId, ipAddress);
            return 1;
        }
        return 0; // 重复报名或数据库错误
    }

    public boolean cancelEnrollment(int activityId, int userId, String ipAddress) {
        boolean success = enrollmentDao.cancelEnroll(activityId, userId);
        if (success) logDao.addLog(userId, "取消了活动报名ID: " + activityId, ipAddress);
        return success;
    }

    public List<User> getEnrollmentList(int activityId) {
        return enrollmentDao.getEnrollUsers(activityId);
    }
}