package math.iterative;

import java.util.Arrays;

public class PerfectSquares {

    public int numSquares(int n) {

        int[] memo = new int[n + 1];
        Arrays.fill(memo, Integer.MAX_VALUE);
        memo[0] = 0;

        for (int i = 1; i * i <= n; i++) {
            int square = i * i;
            for (int j = square; j <= n; j++)
                memo[j] = Math.min(memo[j], memo[j - square] + 1);
        }

        return memo[n];
    }

}
