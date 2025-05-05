package graph.iterative;

import java.util.*;

public class OpenTheLock {

    public int openLock(String[] deadends, String target) {

        Set<String> visited = new HashSet<>(List.of(deadends));
        Queue<String> queue = new ArrayDeque<>();

        if (visited.add("0000")) queue.add("0000");
        int numMoves = 0;
        while (!queue.isEmpty()) {

            int n = queue.size();
            for (int i = 0; i < n; i++) {
                var comb = queue.remove();
                if (comb.equals(target))
                    return numMoves;

                var neighs = getNeighbors(comb, visited);
                visited.addAll(neighs);
                queue.addAll(neighs);
            }

            numMoves++;
        }

        return -1;
    }

    private List<String> getNeighbors(String combination, Set<String> visited) {
        int n               = combination.length();
        List<String> neighs = new ArrayList<>();
        var chars           = combination.toCharArray();

        for (int i = 0; i < n; i++) {
            char ch = combination.charAt(i);
            var prevNeigh = swap(chars, i, ch == '0' ? '9' : (char) (ch - 1));
            var nextNeigh = swap(chars, i, ch == '9' ? '0' : (char) (ch + 1));
            if (!visited.contains(prevNeigh)) neighs.add(prevNeigh);
            if (!visited.contains(nextNeigh)) neighs.add(nextNeigh);
        }

        return neighs;
    }

    private String swap(char[] chars, int idx, char to) {
        char prev = chars[idx];
        chars[idx] = to;
        var s = new String(chars);
        chars[idx] = prev;
        return s;
    }

}
