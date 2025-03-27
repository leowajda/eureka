package array.iterative;

import java.util.HashMap;
import java.util.Map;

public class SubarraySumEqualsK {

    public int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> prefixSum = new HashMap<>();
        prefixSum.put(0, 1);

        int currSum = 0;
        int count   = 0;
        for (var num : nums) {
            currSum += num;
            count   += prefixSum.getOrDefault(currSum - k, 0);
            prefixSum.merge(currSum, 1, Integer::sum);
        }

        return count;
    }

}
