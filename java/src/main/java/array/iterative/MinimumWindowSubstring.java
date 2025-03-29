package array.iterative;

import java.util.stream.IntStream;

public class MinimumWindowSubstring {

    public String minWindow(String s, String t) {

        int[] original = counter(t);
        int[] window   = counter("");

        int minStart        = 0;
        int windowCounter   = 0;
        int minLength       = Integer.MAX_VALUE;
        int originalCounter = (int) IntStream.of(original).filter(num -> num > 0).count();

        for (int leftPtr = 0, rightPtr = 0; rightPtr < s.length(); rightPtr++) {
            var rightCh = s.charAt(rightPtr);
            if (original[rightCh] > 0 && original[rightCh] == ++window[rightCh]) windowCounter++;

            while (windowCounter == originalCounter) {
                if (rightPtr - leftPtr + 1 < minLength) {
                    minLength = rightPtr - leftPtr + 1;
                    minStart  = leftPtr;
                }

                var leftCh = s.charAt(leftPtr++);
                if (original[leftCh] > 0 && --window[leftCh] < original[leftCh]) windowCounter--;
            }

        }

        return minLength == Integer.MAX_VALUE ? "" : s.substring(minStart, minStart + minLength);
    }

    private int[] counter(String s) {
        int n = s.length();
        int[] counter = new int[256];
        for (int i = 0; i < n; i++) counter[s.charAt(i)]++;
        return counter;
    }

}
