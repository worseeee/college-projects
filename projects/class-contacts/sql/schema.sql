CREATE DATABASE IF NOT EXISTS class_contacts_db CHARACTER SET utf8mb4;
USE class_contacts_db;

CREATE TABLE `sys_user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户主键ID',
  `student_no` VARCHAR(20) NOT NULL UNIQUE COMMENT '学号(唯一,用于注册验证)',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
  `password` VARCHAR(64) NOT NULL COMMENT '登录密码(MD5加密)',
  `real_name` VARCHAR(50) NOT NULL COMMENT '真实姓名',
  `phone` VARCHAR(20) COMMENT '手机号码',
  `email` VARCHAR(100) COMMENT '电子邮箱',
  `wechat` VARCHAR(50) COMMENT '微信号',
  `qq` VARCHAR(20) COMMENT 'QQ号',
  `gender` TINYINT DEFAULT 0 COMMENT '性别(0:未知, 1:男, 2:女)',
  `dormitory` VARCHAR(50) COMMENT '宿舍号(如: 12-404)',
  `group_name` VARCHAR(50) COMMENT '小组名称',
  `class_role` VARCHAR(50) DEFAULT '普通学生' COMMENT '班委身份(班长/学委等)',
  `avatar` VARCHAR(255) DEFAULT 'default_avatar.png' COMMENT '头像相对路径',
  `bio` VARCHAR(255) COMMENT '个人简介',
  `status` TINYINT DEFAULT 0 COMMENT '账号状态(0:待审核, 1:正常, 2:禁用)',
  `role` TINYINT DEFAULT 1 COMMENT '系统角色(1:普通学生, 2:管理员)',
  
  -- 隐私控制字段 (0:全班可见, 1:仅好友可见, 2:仅自己可见)
  `privacy_phone` TINYINT DEFAULT 0 COMMENT '手机号隐私权限',
  `privacy_wechat` TINYINT DEFAULT 0 COMMENT '微信号隐私权限',
  `privacy_qq` TINYINT DEFAULT 0 COMMENT 'QQ号隐私权限',
  
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间'
) ENGINE=InnoDB COMMENT='用户信息表';

CREATE TABLE `sys_friendship` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '关系ID',
  `user_id` INT NOT NULL COMMENT '发起申请人ID',
  `friend_id` INT NOT NULL COMMENT '接收申请人ID',
  `status` TINYINT DEFAULT 0 COMMENT '状态(0:申请中, 1:已同意, 2:已拒绝)',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
  CONSTRAINT `fk_friend_user1` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_friend_user2` FOREIGN KEY (`friend_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_user_friend` (`user_id`, `friend_id`) -- 避免重复申请
) ENGINE=InnoDB COMMENT='好友关系表';

CREATE TABLE `sys_collection` (
  `user_id` INT NOT NULL COMMENT '收藏人ID',
  `collected_user_id` INT NOT NULL COMMENT '被收藏人ID',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`user_id`, `collected_user_id`),
  CONSTRAINT `fk_coll_user1` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_coll_user2` FOREIGN KEY (`collected_user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='收藏联系人表';

CREATE TABLE `sys_private_message` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '私信ID',
  `sender_id` INT NOT NULL COMMENT '发送者ID',
  `receiver_id` INT NOT NULL COMMENT '接收者ID',
  `content` TEXT NOT NULL COMMENT '私信内容',
  `is_read` TINYINT DEFAULT 0 COMMENT '阅读状态(0:未读, 1:已读)',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  CONSTRAINT `fk_pm_sender` FOREIGN KEY (`sender_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pm_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='私信聊天表';

CREATE TABLE `sys_board_message` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '留言ID',
  `user_id` INT NOT NULL COMMENT '发布人ID',
  `content` TEXT NOT NULL COMMENT '留言内容',
  `parent_id` INT DEFAULT 0 COMMENT '父留言ID(0为首层留言, 否则为回复)',
  `like_count` INT DEFAULT 0 COMMENT '点赞数',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  CONSTRAINT `fk_board_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='班级留言板表';

CREATE TABLE `sys_photo_album` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '照片ID',
  `user_id` INT NOT NULL COMMENT '上传人ID',
  `photo_url` VARCHAR(255) NOT NULL COMMENT '照片路径',
  `description` VARCHAR(255) COMMENT '照片描述',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  CONSTRAINT `fk_photo_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='班级相册表';

CREATE TABLE `sys_announcement` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '公告ID',
  `admin_id` INT NOT NULL COMMENT '发布管理员ID',
  `title` VARCHAR(100) NOT NULL COMMENT '公告标题',
  `content` TEXT NOT NULL COMMENT '公告正文',
  `category` VARCHAR(20) DEFAULT '通知' COMMENT '分类(活动/通知/作业)',
  `is_top` TINYINT DEFAULT 0 COMMENT '是否置顶(0:否, 1:是)',
  `expire_time` DATETIME COMMENT '失效时间(为空则永久有效)',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  CONSTRAINT `fk_anno_admin` FOREIGN KEY (`admin_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='公告表';

CREATE TABLE `sys_activity` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '活动ID',
  `admin_id` INT NOT NULL COMMENT '发起人ID',
  `title` VARCHAR(100) NOT NULL COMMENT '活动主题',
  `content` TEXT NOT NULL COMMENT '活动详情',
  `activity_time` DATETIME NOT NULL COMMENT '活动举行时间',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  CONSTRAINT `fk_activity_admin` FOREIGN KEY (`admin_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='活动表';

CREATE TABLE `sys_activity_enrollment` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '报名流水ID',
  `activity_id` INT NOT NULL COMMENT '活动ID',
  `user_id` INT NOT NULL COMMENT '报名人ID',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '报名时间',
  CONSTRAINT `fk_enroll_act` FOREIGN KEY (`activity_id`) REFERENCES `sys_activity`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_enroll_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_act_user` (`activity_id`, `user_id`) -- 避免重复报名
) ENGINE=InnoDB COMMENT='活动报名表';

CREATE TABLE `sys_homework` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '作业ID',
  `admin_id` INT NOT NULL COMMENT '发布人ID',
  `title` VARCHAR(100) NOT NULL COMMENT '作业标题',
  `content` TEXT NOT NULL COMMENT '作业要求说明',
  `attachment_url` VARCHAR(255) COMMENT '附件下载路径',
  `deadline` DATETIME NOT NULL COMMENT '截止提交时间',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  CONSTRAINT `fk_homework_admin` FOREIGN KEY (`admin_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='作业中心表';

CREATE TABLE `sys_tag` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '标签ID',
  `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '标签名称'
) ENGINE=InnoDB COMMENT='兴趣标签字典表';

CREATE TABLE `sys_user_tag` (
  `user_id` INT NOT NULL COMMENT '用户ID',
  `tag_id` INT NOT NULL COMMENT '标签ID',
  PRIMARY KEY (`user_id`, `tag_id`),
  CONSTRAINT `fk_ut_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ut_tag` FOREIGN KEY (`tag_id`) REFERENCES `sys_tag`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户-标签多对多关联表';

CREATE TABLE `sys_sensitive_word` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
  `word` VARCHAR(50) NOT NULL UNIQUE COMMENT '敏感词汇'
) ENGINE=InnoDB COMMENT='敏感词库表';

CREATE TABLE `sys_log` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
  `user_id` INT COMMENT '操作人ID(可为空,如未登录拦截)',
  `action` VARCHAR(100) NOT NULL COMMENT '操作动作(如:登录,删帖)',
  `ip_address` VARCHAR(50) COMMENT '客户端IP',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间'
) ENGINE=InnoDB COMMENT='系统操作日志表';
