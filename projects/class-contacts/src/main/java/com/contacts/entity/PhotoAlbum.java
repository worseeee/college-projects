package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//7. 相册实体类 (PhotoAlbum.java)
public class PhotoAlbum implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private Integer userId;
    private String photoUrl;
    private String description;
    private Date createTime;
    
    // 扩展字段
    private String uploaderName;

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

	public String getPhotoUrl() {
		return photoUrl;
	}

	public void setPhotoUrl(String photoUrl) {
		this.photoUrl = photoUrl;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Date getCreateTime() {
		return createTime;
	}

	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}

	public String getUploaderName() {
		return uploaderName;
	}

	public void setUploaderName(String uploaderName) {
		this.uploaderName = uploaderName;
	}

	public static long getSerialversionuid() {
		return serialVersionUID;
	}
}