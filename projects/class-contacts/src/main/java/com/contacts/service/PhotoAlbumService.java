package com.contacts.service;

import com.contacts.dao.LogDao;
import com.contacts.dao.PhotoAlbumDao;
import com.contacts.entity.PhotoAlbum;

import java.util.List;

public class PhotoAlbumService {

    private PhotoAlbumDao photoDao = new PhotoAlbumDao();
    private LogDao logDao = new LogDao();

    public boolean addPhoto(PhotoAlbum photo, String ipAddress) {
        if (photo.getPhotoUrl() == null || photo.getPhotoUrl().isEmpty()) {
            return false;
        }
        boolean success = photoDao.addPhoto(photo);
        if (success) {
            logDao.addLog(photo.getUserId(), "上传了班级相册照片", ipAddress);
        }
        return success;
    }

    public boolean deletePhoto(int id, int userId, int role, String ipAddress) {
        PhotoAlbum photo = photoDao.getPhotoById(id);
        if (photo == null) return false;

        // 权限控制：只能删自己的，管理员能删所有
        if (photo.getUserId() != userId && role != 2) {
            logDao.addLog(userId, "尝试越权删除照片被拦截", ipAddress);
            return false;
        }

        boolean success = photoDao.deletePhoto(id);
        if (success) {
            logDao.addLog(userId, "删除了相册照片ID: " + id, ipAddress);
        }
        return success;
    }

    public PhotoAlbum getPhotoById(int id) {
        return photoDao.getPhotoById(id);
    }

    public List<PhotoAlbum> getPhotoList() {
        return photoDao.getPhotoList();
    }

    public List<PhotoAlbum> getPhotoListByUser(int userId) {
        return photoDao.getPhotoListByUser(userId);
    }
}