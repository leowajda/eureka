package string.iterative;

import java.util.stream.IntStream;

public class DeleteOperationForTwoStrings {

    public int minDistance(String a, String b) {

        int[][] memo = new int[a.length() + 1][b.length() + 1];

        IntStream.rangeClosed(0, b.length()).forEach(col -> memo[0][col] = col);
        IntStream.rangeClosed(0, a.length()).forEach(row -> memo[row][0] = row);

        for (int aPtr = 1; aPtr <= a.length(); aPtr++)
            for (int bPtr = 1; bPtr <= b.length(); bPtr++) {
                char aCh = a.charAt(aPtr - 1);
                char bCh = b.charAt(bPtr - 1);

                memo[aPtr][bPtr] = aCh == bCh ? memo[aPtr - 1][bPtr - 1] : Math.min(memo[aPtr - 1][bPtr] + 1, memo[aPtr][bPtr - 1] + 1);
            }

        return memo[a.length()][b.length()];
    }

}
