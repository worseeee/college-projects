public class charu {
    public static void main(String[] args){
        int[] arr={11,13,14,15,16};
        int[] arrNew=new int[arr.length+1];
        int num=12;
        int index=-1;
        for (int i=0;i<arr.length;i++){
            if(arr[i]>num){
                index=i;
                break;
            }
        }
        for(int i=0;i<arrNew.length;i++){
            if(i<index){
                arrNew[i]=arr[i];
            }else if(i==index){
                arrNew[i]=num;
            }else{
                arrNew[i]=arr[i-1];
            }
        }
        for (int i=0;i<arrNew.length;i++){
            System.out.println(arrNew[i]+" ");
        }
    }
}
