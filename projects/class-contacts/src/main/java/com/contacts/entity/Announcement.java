package com.contacts.entity;

import java.util.Date;

public class Announcement {
    private int id;
    private int adminId;
    private String title;
    private String content;
    private String category; // "通知" 或 "作业"
    private int isTop;
    private Date expireTime;
    private Date createTime;
    private String attachmentUrl; // 发布者上传的原始附件
    
    // 以下为多表关联聚合扩展属性（核心加分项）
    private String adminName;
    private int readCount;       // 已读人数（通知模式）
    private int unreadCount;     // 未读人数（通知模式）
    private int submittedCount;  // 已提交人数（作业模式）
    private int unsubmittedCount;// 未提交人数（作业模式）

    // 完整 Getter 和 Setter
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public int getAdminId() { return adminId; }
    public void setAdminId(int adminId) { this.adminId = adminId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public int getIsTop() { return isTop; }
    public void setIsTop(int isTop) { this.isTop = isTop; }
    public Date getExpireTime() { return expireTime; }
    public void setExpireTime(Date expireTime) { this.expireTime = expireTime; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
    public String getAttachmentUrl() { return attachmentUrl; }
    public void setAttachmentUrl(String attachmentUrl) { this.attachmentUrl = attachmentUrl; }
    public String getAdminName() { return adminName; }
    public void setAdminName(String adminName) { this.adminName = adminName; }
    public int getReadCount() { return readCount; }
    public void setReadCount(int readCount) { this.readCount = readCount; }
    public int getUnreadCount() { return unreadCount; }
    public void setUnreadCount(int unreadCount) { this.unreadCount = unreadCount; }
    public int getSubmittedCount() { return submittedCount; }
    public void setSubmittedCount(int submittedCount) { this.submittedCount = submittedCount; }
    public int getUnsubmittedCount() { return unsubmittedCount; }
    public void setUnsubmittedCount(int unsubmittedCount) { this.unsubmittedCount = unsubmittedCount; }
}