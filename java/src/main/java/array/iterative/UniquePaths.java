package array.iterative;

import java.util.Arrays;

public class UniquePaths {

    public int uniquePaths(int rows, int cols) {
        int[] prev = new int[cols];
        Arrays.fill(prev, 1);

        for (int row = 1; row < rows; row++)
            for (int col = 1; col < cols; col++)
                prev[col] += prev[col - 1];

        return prev[cols - 1];
    }

}
