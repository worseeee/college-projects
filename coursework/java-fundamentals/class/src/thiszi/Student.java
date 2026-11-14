package thiszi;

public class Student {
    private String name;
    private int age;
    public Student(String name,int age){
        this.name=name;
        this.age=age;
    }
    public String read(){
        return "我是："+name+"，年龄："+age;
    }
}
