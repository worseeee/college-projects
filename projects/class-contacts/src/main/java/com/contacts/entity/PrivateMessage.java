package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//3. 私信实体类 (PrivateMessage.java)
public class PrivateMessage implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private Integer senderId;
    private Integer receiverId;
    private String content;
    private Integer isRead; // 0未读, 1已读
    private Date createTime;
    // 扩展字段
    private String senderName;
    private String senderAvatar;
    private String targetName;   // 对端聊天伙伴的姓名
    private String targetAvatar; // 对端聊天伙伴的头像URL
    
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getSenderId() {
		return senderId;
	}
	public void setSenderId(Integer senderId) {
		this.senderId = senderId;
	}
	public Integer getReceiverId() {
		return receiverId;
	}
	public void setReceiverId(Integer receiverId) {
		this.receiverId = receiverId;
	}
	public String getContent() {
		return content;
	}
	public void setContent(String content) {
		this.content = content;
	}
	public Integer getIsRead() {
		return isRead;
	}
	public void setIsRead(Integer isRead) {
		this.isRead = isRead;
	}
	public Date getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}
	public String getSenderName() {
		return senderName;
	}
	public void setSenderName(String senderName) {
		this.senderName = senderName;
	}
	public String getSenderAvatar() {
		return senderAvatar;
	}
	public void setSenderAvatar(String senderAvatar) {
		this.senderAvatar = senderAvatar;
	}
	public static long getSerialversionuid() {
		return serialVersionUID;
	}
	public String getTargetName() { return targetName; }
	public void setTargetName(String targetName) { this.targetName = targetName; }

	public String getTargetAvatar() { return targetAvatar; }
	public void setTargetAvatar(String targetAvatar) { this.targetAvatar = targetAvatar; }
	
	// ==================== 以下为新增的未读数统计字段 ====================
    private int unreadCount; // 该对话框的专属未读消息总数

    public int getUnreadCount() {
        return unreadCount;
    }

    public void setUnreadCount(int unreadCount) {
        this.unreadCount = unreadCount;
    }
}