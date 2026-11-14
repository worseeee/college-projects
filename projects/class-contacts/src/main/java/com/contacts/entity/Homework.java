package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

/**
 * 6. 作业实体类 (Homework.java) - 增强兼容与桥接版
 */
public class Homework implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private Integer adminId;        // 核心物理字段：发布人/教师ID (对应数据库)
    private String title;
    private String content;
    private String attachmentUrl;   // 附件链接
    private Date deadline;
    private Date createTime;
    
    // --- 扩展展示字段 (非数据库物理表字段，用于连表查询时展示老师名字) ---
    private String adminName;
    private String teacherName;

    // --- 原有基础 Getters & Setters ---
    public Integer getId() {
        return id;
    }
    public void setId(Integer id) {
        this.id = id;
    }
    
    public Integer getAdminId() {
        return adminId;
    }
    public void setAdminId(Integer adminId) {
        this.adminId = adminId;
    }
    
    // ==================== 【核心修复：桥接兼容方法】 ====================
    // 让 getTeacherId() / setTeacherId() 直接代理映射到 adminId
    // 彻底解决 Service 层与 Dao 层的命名分歧，实现无感兼容！
    public Integer getTeacherId() {
        return this.adminId;
    }
    public void setTeacherId(Integer teacherId) {
        this.adminId = teacherId;
    }
    // ===================================================================

    public String getTitle() {
        return title;
    }
    public void setTitle(String title) {
        this.title = title;
    }
    
    public String getContent() {
        return content;
    }
    public void setContent(String content) {
        this.content = content;
    }
    
    public String getAttachmentUrl() {
        return attachmentUrl;
    }
    public void setAttachmentUrl(String attachmentUrl) {
        this.attachmentUrl = attachmentUrl;
    }
    
    public Date getDeadline() {
        return deadline;
    }
    public void setDeadline(Date deadline) {
        this.deadline = deadline;
    }
    
    public Date getCreateTime() {
        return createTime;
    }
    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }
    
    // --- 扩展字段 Getters & Setters (同样做了双向同步代理) ---
    public String getAdminName() {
        return adminName != null ? adminName : teacherName;
    }
    public void setAdminName(String adminName) {
        this.adminName = adminName;
        this.teacherName = adminName;
    }
    
    public String getTeacherName() {
        return teacherName != null ? teacherName : adminName;
    }
    public void setTeacherName(String teacherName) {
        this.teacherName = teacherName;
        this.adminName = teacherName;
    }

    public static long getSerialversionuid() {
        return serialVersionUID;
    }
}