package string.recursive;

import java.util.Set;
import java.util.HashSet;
import java.util.stream.IntStream;

import static java.util.stream.Collectors.toCollection;

public class DecodeWays {

    private static final Set<String> VALID_NUMBERS = IntStream.rangeClosed(1, 26)
            .mapToObj(Integer::toString)
            .collect(toCollection(HashSet::new));

    public int numDecodings(String s) {
        return backtrack(s, 0, new Integer[s.length()]);
    }

    private int backtrack(String s, int start, Integer[] memo) {

        if (start >= s.length())
            return 1;

        if (memo[start] != null)
            return memo[start];

        int ways = 0;

        var firstDigit = String.valueOf(s.charAt(start));
        if (VALID_NUMBERS.contains(firstDigit))
            ways += backtrack(s, start + 1, memo);

        if (start + 2 > s.length())
            return memo[start] = ways;

        var secondDigit = String.valueOf(s.charAt(start + 1));
        if (VALID_NUMBERS.contains(firstDigit + secondDigit))
            ways += backtrack(s, start + 2, memo);

        return memo[start] = ways;
    }

}
