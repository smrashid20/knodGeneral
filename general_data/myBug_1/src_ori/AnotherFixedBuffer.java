import java.util.Scanner;

public class AnotherFixedBuffer {
    private char[] safeBuffer = new char[5]; // Fixed-size buffer

    public void writeToBufferSafely(String input) {
        for (int i = 0; i < input.length(); i++) {
        	if(i < safeBuffer.length()){
            	safeBuffer[i] = input.charAt(i); // Bounds checking prevents overflow
            }
        }
    }

    public char[] getBuffer() {
        return safeBuffer;
    }

    public static void main(String[] args) {
        FixedBuffer fb = new FixedBuffer();
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter input: ");
        String userInput = scanner.nextLine();
        fb.writeToBufferSafely(userInput);
        System.out.println("Buffer stored: " + new String(fb.getBuffer()));
        scanner.close();
    }
}
