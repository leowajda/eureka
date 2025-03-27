package array.iterative;

import java.util.Arrays;

public class RangeSumQueryImmutable {

    private final int[] prefixSum;

    public RangeSumQueryImmutable(int[] nums) {
        this.prefixSum = Arrays.copyOf(nums, nums.length);
        for (int i = 1; i < nums.length; i++)
            prefixSum[i] += prefixSum[i - 1];
    }

    public int sumRange(int left, int right) {
        return left == 0 ? prefixSum[right] : prefixSum[right] - prefixSum[left - 1];
    }

}
