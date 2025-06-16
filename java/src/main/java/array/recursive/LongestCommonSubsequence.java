package array.recursive;

import java.util.Arrays;

public class LongestCommonSubsequence {

    public int longestCommonSubsequence(String a, String b) {
        int[][] memo = new int[a.length()][b.length()];
        Arrays.stream(memo).forEach(row -> Arrays.fill(row, Integer.MIN_VALUE));
        return backtrack(a, b, memo, 0, 0);
    }

    private int backtrack(String a, String b, int[][] memo, int ptrA, int ptrB) {
        if (ptrA == a.length() || ptrB == b.length())
            return 0;

        if (memo[ptrA][ptrB] != Integer.MIN_VALUE)
            return memo[ptrA][ptrB];

        if (a.charAt(ptrA) == b.charAt(ptrB))
            return memo[ptrA][ptrB] = backtrack(a, b, memo, ptrA + 1, ptrB + 1) + 1;

        int subA = backtrack(a, b, memo, ptrA + 1, ptrB);
        int subB = backtrack(a, b, memo, ptrA, ptrB + 1);
        return memo[ptrA][ptrB] = Math.max(memo[ptrA][ptrB], Math.max(subA, subB));
    }

}
