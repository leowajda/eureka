package tree.recursive;

import tree.TreeNode;

import java.util.Arrays;
import java.util.Iterator;
import java.util.StringJoiner;

public class SerializeAndDeserializeBinaryTree {

    private static final String DELIMITER = ",";
    private static final String NULL      = "X";

    public String serialize(TreeNode root) {
        StringJoiner sj = new StringJoiner(DELIMITER);
        serializeHelper(root, sj);
        return sj.toString();
    }

    private void serializeHelper(TreeNode root, StringJoiner sj) {
        if (root == null) {
            sj.add(NULL);
            return;
        }

        sj.add(Integer.toString(root.val));
        serializeHelper(root.left, sj);
        serializeHelper(root.right, sj);
    }

    public TreeNode deserialize(String data) {
        var iterator = Arrays.asList(data.split(DELIMITER)).iterator();
        return deserializeHelper(iterator);
    }

    private TreeNode deserializeHelper(Iterator<String> iterator) {
        String value = iterator.next();

        if (value.equals(NULL))
            return null;

        var root   = new TreeNode(Integer.parseInt(value));
        root.left  = deserializeHelper(iterator);
        root.right = deserializeHelper(iterator);
        return root;
    }

}
