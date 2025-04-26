package tree.iterative;

import tree.TreeNode;

import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.ArrayDeque;
import java.util.function.Consumer;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toCollection;

public class BinaryTreeZigzagLevelOrderTraversal {

    public List<List<Integer>> zigzagLevelOrder(TreeNode root) {

        List<List<Integer>> levels = new ArrayList<>();
        Deque<TreeNode> queue      = Stream.ofNullable(root).collect(toCollection(ArrayDeque::new));
        boolean isReversed         = false;

        while (!queue.isEmpty()) {

            int n = queue.size();
            List<Integer> level = new ArrayList<>(n);

            for (int i = 0; i < n; i++) {
                Consumer<Integer> f = isReversed ? level::addFirst : level::addLast;
                var node = queue.remove();

                f.accept(node.val);
                if (node.left != null)  queue.add(node.left);
                if (node.right != null) queue.add(node.right);
            }

            levels.add(level);
            isReversed = !isReversed;
        }

        return levels;
    }

}
