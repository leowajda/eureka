package array.iterative;

import java.util.Arrays;

public class CoinChange {

    public int coinChange(int[] coins, int amount) {

        int[] memo = new int[amount + 1];
        Arrays.fill(memo, Integer.MAX_VALUE);
        memo[0] = 0;

        for (int i = 1; i < memo.length; i++)
            for (var coin : coins) {
                if (i - coin < 0 || memo[i - coin] == Integer.MAX_VALUE) continue;
                memo[i] = Math.min(memo[i], memo[i - coin] + 1);
            }

        return memo[amount] == Integer.MAX_VALUE ? -1 : memo[amount];
    }

}
