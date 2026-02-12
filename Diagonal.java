import java.util.*;

public class Diagonal{
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);
        int dsm = 0;
        int n = sc.nextInt();
        int[][] mat = new int[n][n];
        for(int i=0; i<n; i++){
            for(int j=0; j<n; j++){
                mat[i][j] = sc.nextInt();
            }
        }
        int x = mat.length;
        for(int i=0; i<x; i++){
            dsm += mat[i][i];
            dsm += mat[i][x-1-i];
        }
        if(x % 2 != 0) dsm -= mat[x/2][x/2];
        System.out.println(dsm);
    }
}