# 班级通讯录与班务管理门户

使用 Servlet/JSP、Service/DAO 和 MySQL 构建班级通讯录、公告、作业、活动、相册、留言和审计模块。

**性质**：原生 Java Web 综合课程设计。

## 功能与实现

- 代码按 controller、service、dao、entity、filter、listener 和 utils 分层。
- 登录和管理员 Filter、会话监听、头像流式读取、敏感词处理与审计入口。
- 数据库 DDL 包含 14 类业务表；发布 schema 不含真实用户、消息、密码摘要或种子数据。
- 本地两个相同的 Java 工程合并发布，避免将重复副本计成两个项目。

## 目录与入口

- `sql/schema.sql`
- `src/main/java/com/contacts/controller/ActivityServlet.java`
- `src/main/java/com/contacts/controller/AdminAuditServlet.java`
- `src/main/java/com/contacts/controller/AnnouncementDetailServlet.java`
- `src/main/java/com/contacts/controller/AnnouncementServlet.java`
- `src/main/java/com/contacts/controller/AvatarRenderServlet.java`
- `src/main/java/com/contacts/controller/AvatarUploadServlet.java`
- `src/main/java/com/contacts/controller/BoardServlet.java`
- `src/main/java/com/contacts/controller/BookmarkServlet.java`
- `src/main/java/com/contacts/controller/ContactListServlet.java`
- `src/main/java/com/contacts/controller/FriendshipServlet.java`
- `src/main/java/com/contacts/controller/HomeworkServlet.java`
- `src/main/java/com/contacts/controller/LoginServlet.java`
- `src/main/java/com/contacts/controller/LogoutServlet.java`
- `src/main/java/com/contacts/controller/PhotoAlbumServlet.java`
- `src/main/java/com/contacts/controller/PrivateMessageServlet.java`
- `src/main/java/com/contacts/controller/RegisterServlet.java`
- `src/main/java/com/contacts/controller/UserDetailServlet.java`
- 其余文件见当前目录（共 83 个源码/设计文件）。

## 环境与运行

使用支持 `javax.servlet` 的 Servlet/JSP 容器（原工程为 Tomcat 9 系列），JDK 与 IDE 的 Web 项目配置保持一致。自行添加 MySQL Connector/J 与 JSTL 运行依赖。

1. 在 MySQL 执行 `sql/schema.sql`。
2. 设置环境变量 `CONTACTS_DB_PASSWORD`；数据库地址和用户名在 `DBUtil.java` 中配置。
3. 将 `src/main/java` 编译到 Web 应用 `WEB-INF/classes`，将 `src/main/webapp` 发布为 Web 根目录，再由 Tomcat 启动。
4. 使用新建的测试账号验证各角色功能，不导入个人真实通讯录。

## 验证范围与复现说明

- 当前发布保留原生 MVC 结构，未提供 Maven/Gradle 一键构建；容器与依赖需自行配置。
- 项目属于教学原型；Filter、上传和审计模块存在不代表完成生产安全审计或并发性能测试。
- 原始业务数据库、上传头像、附件与用户数据未发布。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
