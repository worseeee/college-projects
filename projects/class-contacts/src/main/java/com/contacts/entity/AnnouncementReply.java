package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

/**
 * 公告回执/作业提交记录 实体类
 */
public class AnnouncementReply implements Serializable {
    private static final long serialVersionUID = 1L;

    // --- 数据库表基础物理字段 ---
    private Integer id;
    private Integer announcementId; // 关联的公告ID
    private Integer userId;         // 提交人的用户ID
    private String replyContent;    // 文本回复内容
    private String fileUrl;         // 附件路径
    private Date submitTime;        // 提交时间

    // --- 扩展展示字段 (来自 sys_user 连表查询，非数据库本表字段) ---
    private String userName;        // 学生姓名
    private String studentNo;       // 学号
    private String userAvatar;      // 学生头像 (✅ 解决报错的核心字段)

    // ==================== Getters & Setters ====================

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getAnnouncementId() {
        return announcementId;
    }

    public void setAnnouncementId(Integer announcementId) {
        this.announcementId = announcementId;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getReplyContent() {
        return replyContent;
    }

    public void setReplyContent(String replyContent) {
        this.replyContent = replyContent;
    }

    public String getFileUrl() {
        return fileUrl;
    }

    public void setFileUrl(String fileUrl) {
        this.fileUrl = fileUrl;
    }

    public Date getSubmitTime() {
        return submitTime;
    }

    public void setSubmitTime(Date submitTime) {
        this.submitTime = submitTime;
    }

    // --- 扩展字段的 Getters & Setters ---

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getStudentNo() {
        return studentNo;
    }

    public void setStudentNo(String studentNo) {
        this.studentNo = studentNo;
    }

    // ✅ 报错缺少的正是这个方法！
    public String getUserAvatar() {
        return userAvatar;
    }

    public void setUserAvatar(String userAvatar) {
        this.userAvatar = userAvatar;
    }

    public static long getSerialversionuid() {
        return serialVersionUID;
    }
}