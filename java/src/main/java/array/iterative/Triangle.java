package array.iterative;

import java.util.List;

public class Triangle {

    public int minimumTotal(List<List<Integer>> triangle) {

        int rows = triangle.size();

        for (int row = rows - 2; row >= 0; row--) {
            var prevRow = triangle.get(row + 1);
            var currRow = triangle.get(row);

            for (int i = 0; i < currRow.size(); i++) {
                int curr   = currRow.get(i);
                int bottom = prevRow.get(i);
                int right  = prevRow.get(i + 1);

                currRow.set(i, curr + Math.min(bottom, right));
            }

        }

        return triangle.getFirst().getFirst();
    }

}
