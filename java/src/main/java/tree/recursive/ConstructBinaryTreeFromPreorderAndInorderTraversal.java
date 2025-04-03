package tree.recursive;

import tree.TreeNode;

import java.util.HashMap;
import java.util.Map;

public class ConstructBinaryTreeFromPreorderAndInorderTraversal {

    private int currIdx;

    public TreeNode buildTree(int[] preorder, int[] inorder) {
        int n = inorder.length;
        this.currIdx = 0;

        Map<Integer, Integer> inorderMap = new HashMap<>(n);
        for (int idx = 0; idx < n; idx++)
            inorderMap.put(inorder[idx], idx);

        return helper(0, n - 1, preorder, inorderMap);
    }

    private TreeNode helper(int lowIdx, int highIdx, int[] preorder, Map<Integer, Integer> inorderMap) {

        if (lowIdx > highIdx) return null;

        int num = preorder[currIdx++];
        int inorderIdx = inorderMap.get(num);

        var root = new TreeNode(num);
        root.left = helper(lowIdx, inorderIdx - 1, preorder, inorderMap);
        root.right = helper(inorderIdx + 1, highIdx, preorder, inorderMap);

        return root;
    }

}
