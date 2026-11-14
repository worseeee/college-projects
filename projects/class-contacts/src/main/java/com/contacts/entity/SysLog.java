package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//6. 作业实体类 (Homework.java)
public class SysLog implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private Integer userId;
    private String action;
    private String ipAddress;
    private Date createTime;
    
    // 扩展字段
    private String operatorName;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getUserId() {
		return userId;
	}

	public void setUserId(Integer userId) {
		this.userId = userId;
	}

	public String getAction() {
		return action;
	}

	public void setAction(String action) {
		this.action = action;
	}

	public String getIpAddress() {
		return ipAddress;
	}

	public void setIpAddress(String ipAddress) {
		this.ipAddress = ipAddress;
	}

	public Date getCreateTime() {
		return createTime;
	}

	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}

	public String getOperatorName() {
		return operatorName;
	}

	public void setOperatorName(String operatorName) {
		this.operatorName = operatorName;
	}

	public static long getSerialversionuid() {
		return serialVersionUID;
	}
}