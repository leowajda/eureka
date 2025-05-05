package graph.iterative;

import java.util.*;

public class CourseSchedule {

    public boolean canFinish(int numCourses, int[][] prerequisites) {

        Map<Integer, List<Integer>> graph = getGraph(numCourses, prerequisites);
        Map<Integer, Integer> inDegree    = getInDegree(graph, numCourses);
        Queue<Integer> queue              = new ArrayDeque<>();

        for (var entry : inDegree.entrySet())
            if (entry.getValue() == 0)
                queue.add(entry.getKey());

        int counter = 0;
        while (!queue.isEmpty()) {
            var course = queue.remove();
            counter++;

            for (var neigh : graph.get(course)) {
                int degree = inDegree.merge(neigh, -1, Integer::sum);
                if (degree == 0) queue.add(neigh);
            }
        }

        return counter == numCourses;
    }

    private Map<Integer, List<Integer>> getGraph(int numCourses, int[][] reqs) {
        Map<Integer, List<Integer>> graph = new HashMap<>(numCourses);

        for (int course = 0; course < numCourses; course++)
            graph.put(course, new ArrayList<>());

        for (var req : reqs) {
            int to = req[0], from = req[1];
            graph.get(from).add(to);
        }

        return graph;
    }

    private Map<Integer, Integer> getInDegree(Map<Integer, List<Integer>> graph, int numCourses) {
        Map<Integer, Integer> inDegree = new HashMap<>(numCourses);

        for (int course = 0; course < numCourses; course++)
            inDegree.put(course, 0);

        for (var deps : graph.values())
            for (var dep : deps)
                inDegree.merge(dep, 1, Integer::sum);

        return inDegree;
    }

}
