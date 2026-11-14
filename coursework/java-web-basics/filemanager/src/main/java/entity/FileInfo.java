package entity;

public class FileInfo {
    private String fileName;    // 文件名称
    private String uploader;    // 上传用户
    private String uploadTime;  // 上传时间
    private String fileSize;    // 文件大小 (格式化后)
    private String savePath;    // 服务器保存相对路径

    // 构造方法
    public FileInfo(String fileName, String uploader, String uploadTime, String fileSize, String savePath) {
        this.fileName = fileName;
        this.uploader = uploader;
        this.uploadTime = uploadTime;
        this.fileSize = fileSize;
        this.savePath = savePath;
    }

    // Getter 和 Setter 方法
    public String getFileName() { return fileName; }
    public void setFileName(String fileName) { this.fileName = fileName; }

    public String getUploader() { return uploader; }
    public void setUploader(String uploader) { this.uploader = uploader; }

    public String getUploadTime() { return uploadTime; }
    public void setUploadTime(String uploadTime) { this.uploadTime = uploadTime; }

    public String getFileSize() { return fileSize; }
    public void setFileSize(String fileSize) { this.fileSize = fileSize; }

    public String getSavePath() { return savePath; }
    public void setSavePath(String savePath) { this.savePath = savePath; }
}