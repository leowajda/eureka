package graph.iterative;

import java.util.ArrayDeque;
import java.util.List;
import java.util.Queue;
import java.util.function.Consumer;
import java.util.function.Predicate;

public class NumberOfIslands {

    private static final char LAND  = '1';
    private static final char WATER = '0';
    private static final char FLOOD = 'X';

    private record Coordinate(int row, int col) {

        public static final List<Coordinate> deltas = List.of(
                Coordinate.of(0, 1),
                Coordinate.of(0, -1),
                Coordinate.of(1, 0),
                Coordinate.of(-1, 0)
        );

        public static Coordinate of(int row, int col) {
            return new Coordinate(row, col);
        }

        public Coordinate add(Coordinate other) {
            return new Coordinate(other.row + row, other.col + col);
        }
    }

    public int numIslands(char[][] grid) {

        int rows = grid.length, cols = grid[0].length;
        int numIslands = 0;

        for (int row = 0; row < rows; row++)
            for (int col = 0; col < cols; col++)
                if (grid[row][col] == LAND) {
                    flood(grid, Coordinate.of(row, col));
                    numIslands++;
                }

        return numIslands;
    }

    private void flood(char[][] grid, Coordinate start) {

        int rows = grid.length, cols = grid[0].length;
        Queue<Coordinate> queue = new ArrayDeque<>(List.of(start));

        Predicate<Coordinate> isValidNeigh = c -> c.row >= 0 && c.row < rows && c.col >= 0 && c.col < cols;
        Predicate<Coordinate> isLand       = c -> grid[c.row][c.col] == LAND;
        Consumer<Coordinate> flood         = c -> grid[c.row][c.col] = FLOOD;

        flood.accept(start);
        while (!queue.isEmpty()) {
            var node = queue.remove();
            Coordinate.deltas.stream()
                    .map(node::add)
                    .filter(isValidNeigh.and(isLand))
                    .forEach(flood.andThen(queue::add));
        }

    }
}
