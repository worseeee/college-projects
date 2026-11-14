package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//8. 好友关系实体 (Friendship.java)
public class Friendship implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private Integer userId;
    private Integer friendId;
    private Integer status; // 0:申请中, 1:已同意, 2:已拒绝
    private Date createTime;
    
    // 扩展字段
    private String friendName;
    private String friendAvatar;
    private String friendBio;
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
	public Integer getFriendId() {
		return friendId;
	}
	public void setFriendId(Integer friendId) {
		this.friendId = friendId;
	}
	public Integer getStatus() {
		return status;
	}
	public void setStatus(Integer status) {
		this.status = status;
	}
	public Date getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}
	public String getFriendName() {
		return friendName;
	}
	public void setFriendName(String friendName) {
		this.friendName = friendName;
	}
	public String getFriendAvatar() {
		return friendAvatar;
	}
	public void setFriendAvatar(String friendAvatar) {
		this.friendAvatar = friendAvatar;
	}
	public String getFriendBio() {
		return friendBio;
	}
	public void setFriendBio(String friendBio) {
		this.friendBio = friendBio;
	}
	public static long getSerialversionuid() {
		return serialVersionUID;
	}
}