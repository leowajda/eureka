package array.iterative;

public class BinarySearch {

    public int search(int[] nums, int target) {

        int leftPtr = 0;
        int rightPtr = nums.length - 1;

        while (leftPtr <= rightPtr) {
            int midPtr = leftPtr + (rightPtr - leftPtr) / 2;

            if (nums[midPtr] == target)
                return midPtr;

            if (nums[midPtr] < target) leftPtr = midPtr + 1;
            else                       rightPtr = midPtr - 1;
        }

        return -1;
    }

}
