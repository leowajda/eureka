package math.iterative;

public class SqrtX {

    public int mySqrt(int x) {

        long start = 0, end = x;
        long sqrt = -1;

        while (start <= end) {

            long mid = start + (end - start) / 2;

            if (mid * mid == x) return (int) mid;

            if (mid * mid < x) {
                sqrt = mid;
                start = mid + 1;
            } else
                end = mid - 1;

        }

        return (int) sqrt;
    }

}
