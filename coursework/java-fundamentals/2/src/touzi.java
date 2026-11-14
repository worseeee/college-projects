public class touzi {
    public static void main(String[] args) {
        int d = 0, e = 0, f = 0, g = 0, h = 0, o = 0, j = 0, k = 0, l = 0, m = 0, n = 0;
        for (int i = 1; i <= 3600; i++) {
            int a = (int) (6 * Math.random()) + 1;
            int b = (int) (6 * Math.random()) + 1;
            int c = a + b;
            if (c == 2) {
                d++;
            }
            if (c == 3) {
                e++;
            }
            if (c == 4) {
                f++;
            }
            if (c == 5) {
                g++;
            }
            if (c == 6) {
                h++;
            }
            if (c == 7) {
                o++;
            }
            if (c == 8) {
                j++;
            }
            if (c == 9) {
                k++;
            }
            if (c == 10) {
                l++;
            }
            if (c == 11) {
                m++;
            }
            if (c == 12) {
                n++;
            }
        }
        System.out.println("相加的和等于2的次数为" + d);
        System.out.println("相加的和等于3的次数为" + e);
        System.out.println("相加的和等于4的次数为" + f);
        System.out.println("相加的和等于5的次数为" + g);
        System.out.println("相加的和等于6的次数为" + h);
        System.out.println("相加的和等于7的次数为" + o);
        System.out.println("相加的和等于8的次数为" + j);
        System.out.println("相加的和等于9的次数为" + k);
        System.out.println("相加的和等于10的次数为" + l);
        System.out.println("相加的和等于11的次数为" + m);
        System.out.println("相加的和等于12的次数为" + n);
        int[] arr = {d, e, f, g, h, o, j, k, l, m, n};
        int max = arr[0], min = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
            if (arr[i] < min) {
                min = arr[i];
            }
        }
        System.out.println("相加的和的结果次数最多为"+max);
        System.out.println("相加的和的结果次数最少为"+min);
    }
}