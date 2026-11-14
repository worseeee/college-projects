package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//5. 活动实体类 (Activity.java)
public class Activity implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private Integer adminId;
    private String title;
    private String content;
    private Date activityTime;
    private Date createTime;
    
    // 扩展字段
    private String adminName;
    private Integer enrolledCount; // 已报名人数统计
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
	public Date getActivityTime() {
		return activityTime;
	}
	public void setActivityTime(Date activityTime) {
		this.activityTime = activityTime;
	}
	public Date getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}
	public String getAdminName() {
		return adminName;
	}
	public void setAdminName(String adminName) {
		this.adminName = adminName;
	}
	public Integer getEnrolledCount() {
		return enrolledCount;
	}
	public void setEnrolledCount(Integer enrolledCount) {
		this.enrolledCount = enrolledCount;
	}
	public static long getSerialversionuid() {
		return serialVersionUID;
	}
}