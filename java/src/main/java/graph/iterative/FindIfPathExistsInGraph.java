package graph.iterative;

import java.util.*;
import java.util.stream.IntStream;

public class FindIfPathExistsInGraph {

    public boolean validPath(int n, int[][] edges, int source, int destination) {
        Set<Integer> visited              = new HashSet<>(List.of(source));
        Map<Integer, List<Integer>> graph = buildGraph(n, edges);
        Queue<Integer> queue              = new ArrayDeque<>(List.of(source));

        while (!queue.isEmpty()) {
            var node = queue.remove();
            if (node == destination)
                return true;

            for (var neigh : graph.get(node))
                if (visited.add(neigh))
                    queue.add(neigh);
        }

        return false;
    }

    private Map<Integer, List<Integer>> buildGraph(int n, int[][] edges) {
        Map<Integer, List<Integer>> graph = new HashMap<>(n);
        IntStream.range(0, n).forEach(node -> graph.put(node, new ArrayList<>()));

        for (var edge : edges) {
            int from = edge[0];
            int to   = edge[1];
            graph.get(from).add(to);
            graph.get(to).add(from);
        }

        return graph;
    }

}
