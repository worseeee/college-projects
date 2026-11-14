package shuzu;

public class shuzu2 {
    public static void main(String[] args){
        int [][] arr=new int[3][4];
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr[i].length ; j++) {
                arr[i][j]=i*j;
            }
        }
        System.out.println("arr[2][3]="+arr[2][3]);
    }
}
