package array.iterative;

public class FindSmallestLetterGreaterThanTarget {

    public char nextGreatestLetter(char[] letters, char target) {

        int leftPtr = 0;
        int rightPtr = letters.length - 1;
        char nextGreatestLetter = letters[0];

        while (leftPtr <= rightPtr) {

            int midPtr = leftPtr + (rightPtr - leftPtr) / 2;

            if (letters[midPtr] > target) {
                nextGreatestLetter = letters[midPtr];
                rightPtr = midPtr - 1;
            } else
                leftPtr = midPtr + 1;

        }

        return nextGreatestLetter;
    }

}
