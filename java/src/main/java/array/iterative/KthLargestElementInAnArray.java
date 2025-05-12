package array.iterative;

import java.util.PriorityQueue;
import java.util.Queue;

public class KthLargestElementInAnArray {

    public int findKthLargest(int[] nums, int k) {
        Queue<Integer> queue = new PriorityQueue<>(k);

        for (var num : nums) {
            queue.add(num);
            if (queue.size() > k) queue.remove();
        }

        return queue.remove();
    }

}
