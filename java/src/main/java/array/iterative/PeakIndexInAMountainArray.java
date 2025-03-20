package array.iterative;

public class PeakIndexInAMountainArray {

    public int peakIndexInMountainArray(int[] nums) {

        int leftPtr = 0;
        int rightPtr = nums.length - 1;
        int peakPtr = -1;

        while (leftPtr <= rightPtr) {

            int midPtr = leftPtr + (rightPtr - leftPtr) / 2;

            if (nums[midPtr] > nums[midPtr + 1]) {
                peakPtr = midPtr;
                rightPtr = midPtr - 1;
            } else
                leftPtr = midPtr + 1;

        }

        return peakPtr;
    }

}
