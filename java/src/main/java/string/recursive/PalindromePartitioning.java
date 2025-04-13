package string.recursive;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class PalindromePartitioning {

    public List<List<String>> partition(String s) {
        List<List<String>> partitions = new ArrayList<>();
        boolean[][] memo = isPalindrome(s);
        backtrack(s, 0, memo, new ArrayDeque<>(), partitions);
        return partitions;
    }

    private void backtrack(String s, int start, boolean[][] memo, Deque<String> deque, List<List<String>> partitions) {

        if (start >= s.length()) {
            var partition = new ArrayList<>(deque);
            partitions.add(partition);
            return;
        }

        for (int end = start; end < s.length(); end++) {
            if (!memo[start][end]) continue;

            var substring = s.substring(start, end + 1);
            deque.addLast(substring);
            backtrack(s, end + 1, memo, deque, partitions);
            deque.removeLast();
        }

    }

    private boolean[][] isPalindrome(String s) {

        int n = s.length();
        boolean[][] memo = new boolean[n][n];

        for (int end = 0; end < n; end++)
            for (int start = 0; start <= end; start++)
                if (s.charAt(start) == s.charAt(end) && (end - start < 2 || memo[start + 1][end - 1]))
                    memo[start][end] = true;

        return memo;
    }

}
