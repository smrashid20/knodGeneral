import org.junit.runner.JUnitCore;
import org.junit.runner.Request;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;

public class SingleJUnitTestRunner {
    public static void main(String... args) throws ClassNotFoundException {
        if (args.length == 0) {
            System.out.println("Usage: java SingleJUnitTestRunner <TestClass#TestMethod>");
            System.exit(1);
        }

        String[] classAndMethod = args[0].split("#");
        Request request = Request.method(Class.forName(classAndMethod[0]), classAndMethod[1]);

        // Run the specified test case
        Result result = new JUnitCore().run(request);

        // Get test counts
        int totalTests = result.getRunCount();
        int failedTests = result.getFailureCount();
        int passedTests = totalTests - failedTests;

        // Print summary
        System.out.println("Failing tests: " + failedTests);
        System.out.println("Passing tests :" + passedTests);

        // Print failure details if any
        if (!result.wasSuccessful()) {
            System.out.println("\n========== FAILURE DETAILS ==========");
            for (Failure failure : result.getFailures()) {
                System.out.println("Test: " + failure.getTestHeader());  // Test class and method
                System.out.println("Error: " + failure.getMessage());    // Assertion error message
                System.out.println("Stack Trace:\n" + failure.getTrace()); // Full trace for debugging
                System.out.println("-------------------------------------");
            }
        }
    }
}

