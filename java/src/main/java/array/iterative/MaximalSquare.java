package array.iterative;

public class MaximalSquare {

    public int maximalSquare(char[][] matrix) {

        int rows = matrix.length;
        int cols = matrix[0].length;

        int[][] memo = new int[rows][cols];
        int squareSide = 0;

        for (int row = 0; row < rows; row++)
            if (matrix[row][cols - 1] == '1') {
                memo[row][cols - 1] = 1;
                squareSide = 1;
            }

        for (int col = 0; col < cols; col++)
            if (matrix[rows - 1][col] == '1') {
                memo[rows - 1][col] = 1;
                squareSide = 1;
            }

        for (int row = rows - 2; row >= 0; row--)
            for (int col = cols - 2; col >= 0; col--)
                if (matrix[row][col] == '1') {

                    int diag   = memo[row + 1][col + 1];
                    int bottom = memo[row + 1][col];
                    int left   = memo[row][col + 1];

                    memo[row][col] = Math.min(diag, bottom);
                    memo[row][col] = Math.min(memo[row][col], left);
                    memo[row][col] += 1;

                    squareSide = Math.max(squareSide, memo[row][col]);
                }

        return squareSide * squareSide;
    }

}
