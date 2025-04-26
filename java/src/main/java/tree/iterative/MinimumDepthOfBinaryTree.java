package tree.iterative;

import tree.TreeNode;

import java.util.Queue;
import java.util.ArrayDeque;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toCollection;

public class MinimumDepthOfBinaryTree {

    public int minDepth(TreeNode root) {

        int depth = 0;
        Queue<TreeNode> queue = Stream.ofNullable(root).collect(toCollection(ArrayDeque::new));

        while (!queue.isEmpty()) {

            depth++;
            int n = queue.size();

            for (int i = 0; i < n; i++) {
                var node = queue.remove();
                if (node.left == null && node.right == null) return depth;
                if (node.left != null)                       queue.add(node.left);
                if (node.right != null)                      queue.add(node.right);
            }

        }

        return depth;
    }

}
