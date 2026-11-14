package superzi;

public class Dog extends Animal {
    private String color;
    public Dog(String name,int age,String color){
        super(name,age);
        this.setColor(color);
    }
    public String getColor(){
        return color;
    }
    public void setColor(String color){
        this.color=color;
    }
    public String info(){
        return super.info()+"，颜色："+this.getColor();
    }
}
