package graph.iterative;

import java.util.*;

public class SlidingPuzzle {

    private record Board(int[] coords, int zeroPos) {

        private static final int[][] adjacencyList = new int[][]{
                { 1, 3 },
                { 0, 2, 4 },
                { 1, 5 },
                { 0, 4 },
                { 3, 1, 5 },
                {4, 2 }
        };

        public static Board from(int[][] board) {
            int rows     = board.length, cols = board[0].length;
            int[] coords = new int[rows * cols];
            int idx      = 0;
            int zeroPos  = -1;

            for (int row = 0; row < rows; row++)
                for (int col = 0; col < cols; col++) {
                    coords[idx] = board[row][col];
                    if (board[row][col] == 0) zeroPos = idx;
                    idx++;
                }

            return new Board(coords, zeroPos);
        }

        public List<Board> getNeighs() {
            List<Board> boards = new ArrayList<>();

            for (var neigh : adjacencyList[zeroPos]) {
                var newCoords      = Arrays.copyOf(coords, coords.length);
                int prevVal        = newCoords[neigh];
                newCoords[neigh]   = 0;
                newCoords[zeroPos] = prevVal;
                boards.add(new Board(newCoords, neigh));
            }

            return boards;
        }

        @Override
        public boolean equals(Object other) {
            if (this == other) return true;
            if (other == null || getClass() != other.getClass()) return false;
            Board board = (Board) other;
            return zeroPos == board.zeroPos && Arrays.equals(coords, board.coords);
        }

        @Override
        public int hashCode() {
            return Objects.hash(Arrays.hashCode(coords), zeroPos);
        }
    }


    public int slidingPuzzle(int[][] start) {
        int minMoves       = 0;
        Queue<Board> queue = new ArrayDeque<>(List.of(Board.from(start)));
        Set<Board> visited = new HashSet<>(queue);
        var target         = new Board(new int[] { 1, 2, 3, 4, 5, 0 }, 5);

        while (!queue.isEmpty()) {

            int n = queue.size();
            for (int i = 0; i < n; i++) {
                var state = queue.remove();

                if (state.equals(target))
                    return minMoves;

                state.getNeighs()
                        .stream()
                        .filter(visited::add)
                        .forEach(queue::add);
            }

            minMoves++;
        }

        return -1;
    }

}
