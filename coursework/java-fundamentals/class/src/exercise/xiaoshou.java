package exercise;

public class xiaoshou {
    private String name;
    private String writer;
    private int num;

    public xiaoshou(String name, String writer, int num) {
        this.name = name;
        this.writer = writer;
        this.num = num;
    }

    public void read() {
        System.out.println("书名：" + this.name + "作者：" + this.writer + "月销售量：" + this.num);
    }
}