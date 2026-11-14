package com.contacts.entity;

import java.io.Serializable;
import java.util.Date;

/**
 * 用户实体类 (对应 sys_user 表)
 */
public class User implements Serializable {
    private static final long serialVersionUID = 1L;

    private Integer id;
    private String studentNo;
    private String username;
    private String password;
    private String realName;
    private String phone;
    private String email;
    private String wechat;
    private String qq;
    private Integer gender; // 0:未知, 1:男, 2:女
    private String dormitory;
    private String groupName;
    private String classRole;
    private String avatar;
    private String bio;
    private Integer status; // 0:待审, 1:正常, 2:禁用
    private Integer role; // 1:学生, 2:管理员
    
    // 隐私设置 (0:全班可见, 1:仅好友可见, 2:仅自己可见)
    private Integer privacyPhone;
    private Integer privacyWechat;
    private Integer privacyQq;
    
    private Date createTime;
    private Date updateTime;

    // --- 构造方法 ---
    public User() {}

    // --- 下面是通过 Eclipse 自动生成的 Getters 和 Setters ---
    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    
    public String getStudentNo() { return studentNo; }
    public void setStudentNo(String studentNo) { this.studentNo = studentNo; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getRealName() { return realName; }
    public void setRealName(String realName) { this.realName = realName; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getWechat() { return wechat; }
    public void setWechat(String wechat) { this.wechat = wechat; }

    public String getQq() { return qq; }
    public void setQq(String qq) { this.qq = qq; }

    public Integer getGender() { return gender; }
    public void setGender(Integer gender) { this.gender = gender; }

    public String getDormitory() { return dormitory; }
    public void setDormitory(String dormitory) { this.dormitory = dormitory; }

    public String getGroupName() { return groupName; }
    public void setGroupName(String groupName) { this.groupName = groupName; }

    public String getClassRole() { return classRole; }
    public void setClassRole(String classRole) { this.classRole = classRole; }

    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }

    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }

    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }

    public Integer getRole() { return role; }
    public void setRole(Integer role) { this.role = role; }

    public Integer getPrivacyPhone() { return privacyPhone; }
    public void setPrivacyPhone(Integer privacyPhone) { this.privacyPhone = privacyPhone; }

    public Integer getPrivacyWechat() { return privacyWechat; }
    public void setPrivacyWechat(Integer privacyWechat) { this.privacyWechat = privacyWechat; }

    public Integer getPrivacyQq() { return privacyQq; }
    public void setPrivacyQq(Integer privacyQq) { this.privacyQq = privacyQq; }

    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }

    public Date getUpdateTime() { return updateTime; }
    public void setUpdateTime(Date updateTime) { this.updateTime = updateTime; }
    
 // --- 在 User 类中追加以下代码 ---

    // 是否有权发布公告 (0:否, 1:是)
    private int canPublishAnnouncement;

    public int getCanPublishAnnouncement() {
        return canPublishAnnouncement;
    }

    public void setCanPublishAnnouncement(int canPublishAnnouncement) {
        this.canPublishAnnouncement = canPublishAnnouncement;
    }
}