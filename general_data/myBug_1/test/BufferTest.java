import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class BufferTest {
    private BuggyBuffer buggyBuffer;
    private FixedBuffer fixedBuffer;

    @Before
    public void setUp() {
        buggyBuffer = new BuggyBuffer();
        fixedBuffer = new FixedBuffer();
    }

    @Test
    public void testBuggyBufferNoOverflow() {
        buggyBuffer.writeToBuffer("123456"); // Should NOT crash
        assertEquals("12345", new String(fixedBuffer.getBuffer())); // Only first 5 chars stored
    }
}

