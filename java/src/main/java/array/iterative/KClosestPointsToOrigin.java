package array.iterative;

import java.util.Comparator;
import java.util.PriorityQueue;
import java.util.Queue;

public class KClosestPointsToOrigin {

    public int[][] kClosest(int[][] points, int k) {
        Queue<int[]> queue = new PriorityQueue<>(
                Comparator.comparingDouble(KClosestPointsToOrigin::euclideanDistance).reversed()
        );

        for (var point : points) {
            queue.add(point);
            if (queue.size() > k)
                queue.remove();
        }

        return queue.toArray(int[][]::new);
    }

    private static double euclideanDistance(int[] point) {
        int x = point[0], y = point[1];
        return (x * x) + (y * y);
    }

}
