package tree.iterative;

import tree.TreeNode;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.ArrayDeque;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toCollection;

public class BinaryTreeLevelOrderTraversal {

    public List<List<Integer>> levelOrder(TreeNode root) {

        List<List<Integer>> levels = new ArrayList<>();
        Queue<TreeNode> queue      = Stream.ofNullable(root).collect(toCollection(ArrayDeque::new));

        while (!queue.isEmpty()) {
            int n = queue.size();
            List<Integer> level = new ArrayList<>(n);

            for (int i = 0; i < n; i++) {
                var node = queue.remove();
                level.add(node.val);
                if (node.left != null)  queue.add(node.left);
                if (node.right != null) queue.add(node.right);
            }

            levels.add(level);
        }

        return levels;
    }

}
