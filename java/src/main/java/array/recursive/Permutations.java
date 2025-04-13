package array.recursive;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class Permutations {

    private static final int VISITED_MARKER = Integer.MIN_VALUE;

    public List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> permutations = new ArrayList<>();
        backtrack(nums, new ArrayDeque<>(), permutations);
        return permutations;
    }

    private void backtrack(int[] nums, Deque<Integer> deque, List<List<Integer>> permutations) {

        if (deque.size() == nums.length) {
            var permutation = new ArrayList<>(deque);
            permutations.add(permutation);
            return;
        }

        for (int end = 0; end < nums.length; end++) {
            if (nums[end] == VISITED_MARKER) continue;

            deque.addLast(nums[end]);
            nums[end] = VISITED_MARKER;
            backtrack(nums, deque, permutations);
            nums[end] = deque.removeLast();
        }

    }

}
