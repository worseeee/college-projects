public class jiaogu {
    public static void main(String[] args){
        int a=3250;
        while(a!=1){
            if(a%2==0){
                a=a/2;
            }
            else{
                a=a*3+1;
            }
        }
        System.out.println(a);
    }
}
