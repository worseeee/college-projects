package jicheng;

public class Example01 {
    public static void main(String[] args){
        Dog dog=new Dog();
        dog.setName("牧羊犬");
        dog.setAge(3);
        dog.shout();
        dog.printName();
        System.out.println("名称："+dog.getName()+"，年龄："+dog.getAge()+"，颜色："+dog.COLOR);
    }
}
