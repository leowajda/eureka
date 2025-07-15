package array.recursive;

import java.util.Arrays;

public class CoinChangeII {

    public int change(int amount, int[] coins) {
        int[][] memo = new int[coins.length][amount + 1];
        Arrays.stream(memo).forEach(row -> Arrays.fill(row, Integer.MAX_VALUE));
        memo[0][0] = 0;

        int numOfWays = dfs(coins, memo, amount, 0);
        return numOfWays == Integer.MAX_VALUE ? 0 : numOfWays;
    }

    private int dfs(int[] coins, int[][] memo, int amount, int start) {
        if (amount == 0)                              return 1;
        if (amount < 0)                               return 0;
        if (memo[start][amount] != Integer.MAX_VALUE) return memo[start][amount];

        int numOfWays = 0;
        for (int idx = start; idx < coins.length; idx++)
            numOfWays += dfs(coins, memo, amount - coins[idx], idx);

        return memo[start][amount] = numOfWays;
    }

}
