package chouxiang;

public class Example03 {
    public static void main(String[] args) {
        System.out.println("编号"+Animal.getID());
        Dog dog=new Dog();
        dog.info();
        dog.shout();
        dog.eat();
    }
}
