package string.iterative;

import java.util.stream.IntStream;

public class EditDistance {

    public int minDistance(String a, String b) {

        int[][] memo = new int[a.length() + 1][b.length() + 1];

        IntStream.rangeClosed(0, a.length())
                .forEach(row -> memo[row][0] = row);

        IntStream.rangeClosed(0, b.length())
                .forEach(col -> memo[0][col] = col);

        for (int aPtr = 1; aPtr < memo.length; aPtr++) {
            for (int bPtr = 1; bPtr < memo[0].length; bPtr++) {

                char aChar = a.charAt(aPtr - 1);
                char bChar = b.charAt(bPtr - 1);

                if (aChar == bChar) {
                    memo[aPtr][bPtr] = memo[aPtr - 1][bPtr - 1];
                    continue;
                }

                memo[aPtr][bPtr] = Math.min(
                        memo[aPtr - 1][bPtr],
                        Math.min(memo[aPtr][bPtr - 1], memo[aPtr - 1][bPtr - 1])
                );

                memo[aPtr][bPtr] += 1;
            }
        }

        return memo[a.length()][b.length()];
    }

}
