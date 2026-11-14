package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//2. 留言板实体类 (BoardMessage.java)
public class BoardMessage implements Serializable {

    private static final long serialVersionUID = 1L;

    private Integer id;
    private Integer userId;
    private String content;
    private Integer parentId;
    private Integer likeCount;
    private Date createTime;
    
    // --- 扩展字段 (用于JSP页面展示，数据库中无此列) ---
    private String authorName;   // 发布人姓名
    private String authorAvatar; // 发布人头像
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
	public String getContent() {
		return content;
	}
	public void setContent(String content) {
		this.content = content;
	}
	public Integer getParentId() {
		return parentId;
	}
	public void setParentId(Integer parentId) {
		this.parentId = parentId;
	}
	public Integer getLikeCount() {
		return likeCount;
	}
	public void setLikeCount(Integer likeCount) {
		this.likeCount = likeCount;
	}
	public Date getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}
	public String getAuthorName() {
		return authorName;
	}
	public void setAuthorName(String authorName) {
		this.authorName = authorName;
	}
	public String getAuthorAvatar() {
		return authorAvatar;
	}
	public void setAuthorAvatar(String authorAvatar) {
		this.authorAvatar = authorAvatar;
	}
	public static long getSerialversionuid() {
		return serialVersionUID;
	}
	// 留言的回复列表 (非数据库字段，用于前端嵌套渲染)
    private java.util.List<BoardMessage> replies;

    public java.util.List<BoardMessage> getReplies() {
        return replies;
    }

    public void setReplies(java.util.List<BoardMessage> replies) {
        this.replies = replies;
    }
}