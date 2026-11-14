package chouxiang;

public interface Animal {
    int ID=1;
    String NAME="牧羊犬";
    void shout();
    public void info();
    static int getID(){
        return Animal.ID;
    }
}
