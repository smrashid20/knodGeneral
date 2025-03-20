package org.example;

public class Sample {
    private int count = 10;
    public String message = "Hello, world!";

    public Sample() {
        char initial = 'A';
        System.out.println("Constructor called with initial: " + initial);
    }

    public void sayHello(String name) {
        System.out.println("Hello " + name);
    }

    public int addNumbers(int a, int b) {
        return a + b;
    }

    public double addNumbers(int a) {
        return a + 2.5;
    }

    public static void main(String[] args) {
        Sample obj = new Sample();
        obj.sayHello("Alice");
        int sum = obj.addNumbers(5, 5);
        System.out.println("Sum: " + sum);
    }
}
