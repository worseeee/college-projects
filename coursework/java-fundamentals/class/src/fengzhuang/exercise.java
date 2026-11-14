package fengzhuang;

public class exercise {
    private String name;
    private String sex;
    public String getName(){
        return name;
    }
    public void setName(String name){
        this.name=name;
    }
    public String getSex(){
        return sex;
    }
    public void setSex(String sex){
        this.sex=sex;
    }
    void read(){
        System.out.println(name+"性别是："+sex);
    }
}
