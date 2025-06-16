package array.iterative;

import java.util.Arrays;

public class LongestIncreasingSubsequence {

    public int lengthOfLIS(int[] nums) {

        int n       = nums.length;
        int lis     = 0;
        int[] memo  = new int[n];
        Arrays.fill(memo, 1);

        for (int i = n - 1; i >= 0; i--) {
            for (int j = i + 1; j < n; j++)
                if (nums[i] < nums[j])
                    memo[i] = Math.max(memo[i], memo[j] + 1);

            lis = Math.max(lis, memo[i]);
        }


        return lis;
    }

}
