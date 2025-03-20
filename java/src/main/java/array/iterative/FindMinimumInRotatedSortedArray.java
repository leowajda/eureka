package array.iterative;

public class FindMinimumInRotatedSortedArray {

    public int findMin(int[] nums) {

        int leftPtr = 0;
        int midPtr = -1;
        int rightPtr = nums.length - 1;

        while (leftPtr <= rightPtr) {

            midPtr = leftPtr + (rightPtr - leftPtr) / 2;

            if (midPtr > 0 && nums[midPtr - 1] > nums[midPtr])
                return nums[midPtr];

            if (nums[midPtr] > nums[rightPtr]) leftPtr = midPtr + 1;
            else                               rightPtr = midPtr - 1;
        }

        return nums[midPtr];
    }

}
