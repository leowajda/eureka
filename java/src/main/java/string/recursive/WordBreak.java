package string.recursive;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class WordBreak {

    public boolean wordBreak(String s, List<String> wordDict) {
        return backtrack(s, 0, new HashSet<>(wordDict), new Boolean[s.length()]);
    }

    private boolean backtrack(String s, int start, Set<String> wordDict, Boolean[] memo) {

        if (start >= s.length())
            return true;

        if (memo[start] != null)
            return memo[start];

        for (int end = start; end < s.length(); end++) {
            var word = s.substring(start, end + 1);
            if (wordDict.contains(word) && backtrack(s, end + 1, wordDict, memo))
                return memo[start] = true;
        }

        return memo[start] = false;
    }

}
