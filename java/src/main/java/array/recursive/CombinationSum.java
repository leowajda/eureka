package array.recursive;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class CombinationSum {

    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        List<List<Integer>> combinations = new ArrayList<>();
        backtrack(candidates, 0, target, new ArrayDeque<>(), combinations);
        return combinations;
    }

    private void backtrack(int[] candidates, int start, int target, Deque<Integer> deque, List<List<Integer>> combinations) {

        if (target == 0) {
            var combination = new ArrayList<>(deque);
            combinations.add(combination);
            return;
        }

        for (int end = start; end < candidates.length; end++) {
            if (target - candidates[end] < 0) continue;
            deque.addLast(candidates[end]);
            backtrack(candidates, end, target - candidates[end], deque, combinations);
            deque.removeLast();
        }

    }

}
