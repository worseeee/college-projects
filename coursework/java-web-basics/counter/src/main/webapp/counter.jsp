<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%
    // 1. 定义锁对象，防止高并发访问导致计数不准确
    Object counterLock = application.getAttribute("counterLock");
    if(counterLock == null){
        counterLock = new Object();
        application.setAttribute("counterLock", counterLock);
    }

    // 2. 检查用户是不是第一次访问 (基于 session)
    String isVisited = (String) session.getAttribute("isVisited");
    
    // 如果 isVisited 为 null，说明这是此用户开启浏览器后的第一次访问
    if (isVisited == null) {
        synchronized(counterLock) { // 同步锁，防止多线程写入冲突
            // 从 application 中获取总访问量
            Integer totalCount = (Integer) application.getAttribute("totalCount");
            if (totalCount == null) {
                totalCount = 1; // 网站第一次被访问
            } else {
                totalCount = totalCount + 1;
            }
            // 更新全局变量
            application.setAttribute("totalCount", totalCount);
        }
        // ★关键：在这个用户的 session 中打上标记！
        session.setAttribute("isVisited", "true");
    }
    
    // 取出最新的总访问量（哪怕是按F5，拿到的也是之前存入的数量）
    Integer currentCount = (Integer) application.getAttribute("totalCount");
%>
<!DOCTYPE html>
<html>
<head>
    <title>JSP 图片计数器</title>
    <style>
        body { font-family: "Microsoft YaHei"; text-align: center; padding-top: 50px; background: #eef2f3; }
        .counter-panel { display: inline-block; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .images-container { margin: 20px 0; padding: 15px; background: #222; border-radius: 5px; display: inline-block; }
        /* 约束图片大小，确保排列整齐 */
        .images-container img { width: 30px; height: 40px; margin: 0 2px; }
        .tips { color: #666; font-size: 14px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="counter-panel">
        <h2>您好！您是本站的第</h2>
        
        <div class="images-container">
            <%
                // 3. 将数字转换为图片 HTML
                if (currentCount != null) {
                    // 把数字如 158 转换成字符串 "158"
                    String countStr = String.valueOf(currentCount);
                    
                    // 遍历字符串的每一个字符
                    for (int i = 0; i < countStr.length(); i++) {
                        char digit = countStr.charAt(i); // 获取单个字符 '1', '5', '8'
                        // 动态拼接出 <img> 标签，路径指向 images/ 目录下的图片
                        out.print("<img src='images/" + digit + ".png' alt='" + digit + "'>");
                    }
                }
            %>
        </div>
        
        <h2>位访客</h2>
        
        <div class="tips">
            <p>💡 提示：按 F5 刷新本页面，数字不会增加，因为您的 session 被识别为已访问。</p>
            <p>想要测试增加数字？请使用浏览器的“无痕/隐身模式”或换个浏览器打开。</p>
        </div>
    </div>
</body>
</html>