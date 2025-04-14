package array.recursive;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class Subsets {

    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> subsets = new ArrayList<>();
        backtrack(nums, 0, new ArrayDeque<>(), subsets);
        return subsets;
    }

    private void backtrack(int[] nums, int idx, Deque<Integer> deque, List<List<Integer>> subsets) {

        if (idx == nums.length) {
            var subset = new ArrayList<>(deque);
            subsets.add(subset);
            return;
        }

        deque.addLast(nums[idx]);
        backtrack(nums, idx + 1, deque, subsets);
        deque.removeLast();
        backtrack(nums, idx + 1, deque, subsets);
    }

}
