package custom.iterative;

import java.util.Comparator;
import java.util.PriorityQueue;
import java.util.Queue;

public class FindMedianFromDataStream {

    private final Queue<Integer> left;
    private final Queue<Integer> right;
    private boolean isEven;

    public FindMedianFromDataStream() {
        this.left   = new PriorityQueue<>(Comparator.reverseOrder());
        this.right  = new PriorityQueue<>();
        this.isEven = true;
    }

    public void addNum(int num) {
        if (isEven) {
            right.add(num);
            left.add(right.remove());
        } else {
            left.add(num);
            right.add(left.remove());
        }

        isEven = !isEven;
    }

    public double findMedian() {
        return isEven ? ((left.peek() + right.peek()) / 2.0) : left.peek();
    }

}
