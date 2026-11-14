package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//10. 活动报名流水 (ActivityEnrollment.java)
public class ActivityEnrollment implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private Integer activityId;
    private Integer userId;
    private Date createTime;
    
    // 扩展字段
    private String enrollUserName;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getActivityId() {
		return activityId;
	}

	public void setActivityId(Integer activityId) {
		this.activityId = activityId;
	}

	public Integer getUserId() {
		return userId;
	}

	public void setUserId(Integer userId) {
		this.userId = userId;
	}

	public Date getCreateTime() {
		return createTime;
	}

	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}

	public String getEnrollUserName() {
		return enrollUserName;
	}

	public void setEnrollUserName(String enrollUserName) {
		this.enrollUserName = enrollUserName;
	}

	public static long getSerialversionuid() {
		return serialVersionUID;
	}
}