package array.iterative;

public class FindFirstAndLastPositionOfElementInSortedArray {

    public int[] searchRange(int[] nums, int target) {
        int firstPosition = firstPosition(nums, target);
        int lastPosition  = lastPosition(nums, target);

        return new int[] { firstPosition, lastPosition };
    }

    private int firstPosition(int[] nums, int target) {

        int leftPtr = 0;
        int rightPtr = nums.length - 1;
        int firstPosition = -1;

        while (leftPtr <= rightPtr) {

            int midPtr = leftPtr + (rightPtr - leftPtr) / 2;

            if (nums[midPtr] >= target) {
                if (nums[midPtr] == target) firstPosition = midPtr;
                rightPtr = midPtr - 1;
            } else
                leftPtr = midPtr + 1;

        }

        return firstPosition;
    }

    private int lastPosition(int[] nums, int target) {

        int leftPtr = 0;
        int rightPtr = nums.length - 1;
        int lastPosition = -1;

        while (leftPtr <= rightPtr) {

            int midPtr = leftPtr + (rightPtr - leftPtr) / 2;

            if (nums[midPtr] <= target) {
                if (nums[midPtr] == target) lastPosition = midPtr;
                leftPtr = midPtr + 1;
            } else
                rightPtr = midPtr - 1;

        }

        return lastPosition;
    }

}
