package array.recursive;

public class BurstBalloons {

    public int maxCoins(int[] nums) {

        int n        = nums.length;
        int[][] memo = new int[n][n];

        return backtrack(nums, memo, 0, n - 1);
    }

    private int backtrack(int[] nums, int[][] memo, int left, int right) {

        if (left > right)
            return 0;

        if (memo[left][right] != 0)
            return memo[left][right];

        for (int i = left; i <= right; i++) {

            int currBalloon  = nums[i];
            int leftBalloon  = left - 1 == -1 ? 1 : nums[left - 1];
            int rightBalloon = right + 1 == nums.length ? 1 : nums[right + 1];

            memo[left][right] = Math.max(
                    memo[left][right],
                    backtrack(nums, memo, left, i - 1) + (leftBalloon * currBalloon * rightBalloon) + backtrack(nums, memo, i + 1, right)
            );

        }

        return memo[left][right];
    }

}
