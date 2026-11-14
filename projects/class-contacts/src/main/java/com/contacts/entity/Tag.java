package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

//9. 兴趣标签 (Tag.java)
public class Tag implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private String name;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public static long getSerialversionuid() {
		return serialVersionUID;
	}
}