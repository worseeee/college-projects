# FileManager Java Web 练习

Servlet 文件上传、列表与下载

**性质**：Servlet/JSP 分项实验。

## 功能与实现

- Servlet 文件上传、列表与下载。
- 与班级门户分开保留，便于查看单模块实现。

## 目录与入口

- `src/main/java/entity/FileInfo.java`
- `src/main/java/servlet/DownloadServlet.java`
- `src/main/java/servlet/FileListServlet.java`
- `src/main/java/servlet/UploadServlet.java`
- `src/main/webapp/WEB-INF/web.xml`
- `src/main/webapp/css/style.css`
- `src/main/webapp/fileList.jsp`
- `src/main/webapp/index.jsp`
- `src/main/webapp/uploadResult.jsp`

## 环境与运行

在兼容 javax.servlet 的 Servlet/JSP 容器中配置 Web 应用，编译 src/main/java 并部署 src/main/webapp。依赖容器 API，不将容器 JAR 提交到仓库。

## 验证范围与复现说明

- 上传文件、容器部署目录和 Eclipse .metadata 未发布。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../../README.md)
