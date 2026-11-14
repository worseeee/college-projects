<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<table class="file-table">
    <thead>
        <tr>
            <th>文件名称</th>
            <th>上传用户</th>
            <th>上传时间</th>
            <th>文件大小</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        <c:if test="${empty fileList}">
            <tr>
                <td colspan="5" style="color: #999;">暂无文件记录，快去上传一个吧！</td>
            </tr>
        </c:if>
        
        <c:forEach items="${applicationScope.globalFileList}" var="file">
            <tr>
                <td style="color:#0056b3; max-width: 200px; word-wrap: break-word;">${file.fileName}</td>
                <td>${file.uploader}</td>
                <td style="font-size: 12px; color: #666;">${file.uploadTime}</td>
                <td>${file.fileSize}</td>
                <td>
                    <a href="download?fileName=${file.fileName}" class="download-link">下载</a>
                </td>
            </tr>
        </c:forEach>
    </tbody>
</table>