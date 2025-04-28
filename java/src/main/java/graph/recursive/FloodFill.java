package graph.recursive;

public class FloodFill {

    public int[][] floodFill(int[][] image, int sr, int sc, int color) {
        if (image[sr][sc] == color) return image;
        dfs(image, sr, sc, image[sr][sc], color);
        return image;
    }

    private void dfs(int[][] image, int row, int col, int from, int to) {
        if (row < 0 || row >= image.length || col < 0 || col >= image[0].length || image[row][col] != from) return;
        image[row][col] = to;
        dfs(image, row + 1, col, from, to);
        dfs(image, row - 1, col, from, to);
        dfs(image, row, col + 1, from, to);
        dfs(image, row, col - 1, from, to);
    }

}
