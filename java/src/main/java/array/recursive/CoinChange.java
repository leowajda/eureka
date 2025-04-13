package array.recursive;

public class CoinChange {

    public int coinChange(int[] coins, int amount) {
        int coinChange = backtrack(coins, amount, new Integer[amount + 1]);
        return coinChange == Integer.MAX_VALUE ? -1 : coinChange;
    }

    private int backtrack(int[] coins, int amount, Integer[] memo) {

        if (amount == 0)
            return 0;

        if (memo[amount] != null)
            return memo[amount];

        int minCoinChange = Integer.MAX_VALUE;
        for (var coin : coins) {
            if (amount - coin < 0) continue;

            int coinChange = backtrack(coins, amount - coin, memo);
            if (coinChange == Integer.MAX_VALUE) continue;
            minCoinChange = Math.min(minCoinChange, coinChange + 1);
        }

        return memo[amount] = minCoinChange;
    }

}
