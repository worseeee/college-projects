package com.contacts.service;

import com.contacts.dao.AnnouncementDao;
import com.contacts.dao.LogDao;
import com.contacts.entity.Announcement;

import java.util.List;

public class AnnouncementService {

    private AnnouncementDao announcementDao = new AnnouncementDao();
    private LogDao logDao = new LogDao();

    private boolean checkAdmin(int role) {
        return role == 2;
    }

    public boolean addAnnouncement(Announcement announcement, int userRole, String ipAddress) {
        if (!checkAdmin(userRole)) return false;
        boolean success = announcementDao.addAnnouncement(announcement);
        if (success) {
            logDao.addLog(announcement.getAdminId(), "发布了新公告: " + announcement.getTitle(), ipAddress);
        }
        return success;
    }

    public boolean updateAnnouncement(Announcement announcement, int userRole, String ipAddress) {
        if (!checkAdmin(userRole)) return false;
        boolean success = announcementDao.updateAnnouncement(announcement);
        if (success) {
            logDao.addLog(announcement.getAdminId(), "更新了公告ID: " + announcement.getId(), ipAddress);
        }
        return success;
    }

    public boolean deleteAnnouncement(int id, int adminId, int userRole, String ipAddress) {
        if (!checkAdmin(userRole)) return false;
        boolean success = announcementDao.deleteAnnouncement(id);
        if (success) {
            logDao.addLog(adminId, "删除了公告ID: " + id, ipAddress);
        }
        return success;
    }

    public Announcement getAnnouncementById(int id) {
        return announcementDao.getAnnouncementById(id);
    }

    public List<Announcement> getValidAnnouncements() {
        return announcementDao.getValidAnnouncements();
    }

    public List<Announcement> getTopAnnouncements() {
        return announcementDao.getTopAnnouncements();
    }
}