package staticzi;

public class Example05 {
    public static void main(String[] args) {
        Student stu1=new Student("张三",18);
        Student stu2=new Student("李四",19);
        Student stu3=new Student("王五",20);
        stu1.info();
        stu2.info();
        stu3.info();
        stu1.school="B大学";
        System.out.println("修改stu1学生对象的学校信息为B大学后");
        stu1.info();
        stu2.info();
        stu3.info();
    }
}
