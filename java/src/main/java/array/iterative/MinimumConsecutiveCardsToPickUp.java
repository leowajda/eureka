package array.iterative;

import java.util.stream.IntStream;

public class MinimumConsecutiveCardsToPickUp {

    public int minimumCardPickup(int[] cards) {

        int minMoves  = Integer.MAX_VALUE;
        int maxCard   = IntStream.of(cards).max().orElse(0);
        int[] counter = new int[maxCard + 1];

        for (int leftPtr = 0, rightPtr = 0; rightPtr < cards.length; rightPtr++) {
            counter[cards[rightPtr]] += 1;

            while (counter[cards[rightPtr]] == 2) {
                minMoves = Math.min(minMoves, rightPtr - leftPtr + 1);
                counter[cards[leftPtr]] -= 1;
                leftPtr++;
            }
        }

        return minMoves == Integer.MAX_VALUE ? -1 : minMoves;
    }

}
