package array.iterative;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class LargestDivisibleSubset {

    public List<Integer> largestDivisibleSubset(int[] nums) {

        int n         = nums.length;
        int max       = 0;
        int[] counter = new int[n];
        int[] prev    = new int[n];

        Arrays.sort(nums);
        Arrays.fill(counter, 1);
        Arrays.fill(prev, -1);

        for (int i = n - 1; i >= 0; i--) {
            for (int j = i + 1; j < n; j++)
                if (nums[j] % nums[i] == 0 && counter[i] <= counter[j] + 1) {
                    counter[i] = counter[j] + 1;
                    prev[i]    = j;
                }

            if (counter[i] > counter[max]) max = i;
        }

        return buildList(prev, nums, max);
    }

    private List<Integer> buildList(int[] prev, int[] nums, int curr) {

        List<Integer> list = new ArrayList<>();
        int ptr = curr;

        while (ptr != -1) {
            list.add(nums[ptr]);
            ptr = prev[ptr];
        }

        return list;
    }

}
