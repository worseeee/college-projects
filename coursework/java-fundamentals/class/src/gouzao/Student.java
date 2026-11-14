package gouzao;

public class Student {
    private String name;
    private int age;
    public Student(String n,int a){
        name=n;
        age=a;
        System.out.println("调用了有参构造方法");
    }
    public void read(){
        System.out.println("我是："+name+"，年龄："+age);
    }
}
