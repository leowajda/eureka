package string.recursive;

import java.util.ArrayList;
import java.util.List;

public class GenerateParentheses {

    public List<String> generateParenthesis(int n) {
        List<String> parenthesis = new ArrayList<>();
        backtrack(n, n, new StringBuilder(), parenthesis);
        return parenthesis;
    }

    private void backtrack(int open, int close, StringBuilder sb, List<String> parenthesis) {

        if (open == 0 && close == 0) {
            parenthesis.add(sb.toString());
            return;
        }

        int n = sb.length();
        if (open > 0) {
            sb.append("(");
            backtrack(open - 1, close, sb, parenthesis);
            sb.deleteCharAt(n);
        }

        if (close > open) {
            sb.append(")");
            backtrack(open, close - 1, sb, parenthesis);
            sb.deleteCharAt(n);
        }

    }

}
