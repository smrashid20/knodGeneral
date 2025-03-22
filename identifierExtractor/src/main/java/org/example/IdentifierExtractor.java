package org.example;

import com.github.javaparser.*;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.nodeTypes.NodeWithSimpleName;
import com.github.javaparser.ast.type.*;
import com.github.javaparser.ast.Node;

import java.io.*;
import java.lang.reflect.Type;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import com.google.gson.GsonBuilder;

public class IdentifierExtractor {
    private static final Map<String, CompilationUnit> parsedFiles = new HashMap<>(); // Store parsed files

    private static Map<String, List<String>> classHierarchy = new HashMap<>();


    public static void main(String[] args) {
        // Check for required arguments
        if (args.length < 2) {
            System.out.println("Usage: java IdentifierExtractor <project_folder> <source_file> [append_mode (0 or 1)]");
            return;
        }

        String projectFolderName = args[0];
        String sourceFilePath = args[1];
        int appendMode = (args.length > 2) ? Integer.parseInt(args[2]) : 0; // Default: Overwrite (0)

        File projectFolder = new File(projectFolderName);
        File mainFile = new File(sourceFilePath);

        if (!projectFolder.exists() || !projectFolder.isDirectory()) {
            System.out.println("Error: Invalid project folder.");
            return;
        }

        if (!mainFile.exists() || !mainFile.getName().endsWith(".java")) {
            System.out.println("Error: Invalid source file.");
            return;
        }

        // Initialize extracted data map
        Map<String, Map<String, List<Map<String, Object>>>> extractedData = new LinkedHashMap<>();
        int nextFileId = 1;

        File jsonFile = new File("identifiers.json");
        Gson gson = new GsonBuilder().disableHtmlEscaping().setPrettyPrinting().create();
        Type type = new TypeToken<Map<String, Map<String, List<Map<String, Object>>>>>() {}.getType();

        // Load existing data if appending
        if (appendMode == 1 && jsonFile.exists()) {
            try (Reader reader = new FileReader(jsonFile)) {
                extractedData = gson.fromJson(reader, type);
                if (extractedData != null && !extractedData.isEmpty()) {
                    nextFileId = extractedData.keySet().stream()
                            .mapToInt(Integer::parseInt)
                            .max()
                            .orElse(0) + 1;
                }
            } catch (IOException e) {
                System.out.println("Warning: Could not read existing identifiers.json, creating a new one.");
                extractedData = new LinkedHashMap<>();
            }
        }

        extractedData.put(String.valueOf(nextFileId), new LinkedHashMap<>());

        // Parse all Java files in the project folder
        parseProjectFiles(projectFolder);

        // Extract identifiers from the main file and any referenced files
        extractIdentifiers(mainFile, extractedData, nextFileId);

        // 🔹 Handle duplicates before writing to JSON
        extractedData.put(String.valueOf(nextFileId), mergeDuplicateEntries(extractedData.get(String.valueOf(nextFileId))));

        //Length of extractedData
        System.out.println("Extracted data length: " + extractedData.get(String.valueOf(nextFileId)).size());

        // Save the extracted data to identifiers.json
        try (FileWriter writer = new FileWriter(jsonFile)) {
            gson.toJson(extractedData, writer);
        } catch (IOException e) {
            System.out.println("Error: Failed to write to identifiers.json");
            e.printStackTrace();
        }

        System.out.println("\nIdentifiers extracted and saved to 'identifiers.json'.");
    }

    /**
     * Merges duplicate entries in extracted identifiers by summing "cnt" values
     * and removing redundant superclass definitions when already inherited.
     */
    public static Map<String, List<Map<String, Object>>> mergeDuplicateEntries(Map<String, List<Map<String, Object>>> data) {
        Map<String, List<Map<String, Object>>> mergedData = new LinkedHashMap<>();

        for (Map.Entry<String, List<Map<String, Object>>> entry : data.entrySet()) {
            String identifier = entry.getKey();
            List<Map<String, Object>> uniqueEntries = new ArrayList<>();
            Map<Integer, Map<String, Object>> mergedEntries = new HashMap<>();

            for (Map<String, Object> item : entry.getValue()) {
                // Copy the map and remove the 'cnt' property for hashing
                Map<String, Object> itemCopy = new LinkedHashMap<>(item);
                itemCopy.remove("cnt");

                // Generate a hash of the properties (excluding 'cnt')
                int hash = itemCopy.hashCode();

                if (mergedEntries.containsKey(hash)) {
                    // Merge cnt values if duplicate found
                    Map<String, Object> existingEntry = mergedEntries.get(hash);
                    existingEntry.put("cnt", (int) existingEntry.get("cnt") + (int) item.get("cnt"));
                } else {
                    // Otherwise, store as a new unique entry
                    Map<String, Object> newEntry = new LinkedHashMap<>(item);
                    mergedEntries.put(hash, newEntry);
                }
            }

            // Convert merged map values to list
            uniqueEntries.addAll(mergedEntries.values());
            mergedData.put(identifier, uniqueEntries);
        }

        return mergedData;
    }




    private static void parseProjectFiles(File projectFolder) {
        try {
            Files.walk(projectFolder.toPath())
                    .filter(path -> path.toString().endsWith(".java"))
                    .forEach(path -> {
                        try {
                            CompilationUnit cu = StaticJavaParser.parse(path.toFile());
                            String className = getClassName(cu);
                            if (className != null) {
                                parsedFiles.put(className, cu); // Store parsed class
                            }
                        } catch (IOException e) {
                            System.err.println("Failed to parse file: " + path);
                        }
                    });
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private static void extractIdentifiers(File javaFile, Map<String, Map<String, List<Map<String, Object>>>> data, int fileId) {
        String fileKey = String.valueOf(fileId);

        // Ensure file ID entry exists in the data map
        data.putIfAbsent(fileKey, new LinkedHashMap<>());

        Map<String, Integer> methodUsageCount = new HashMap<>();  // Track method usage per file
        Map<String, Integer> variableUsageCount = new HashMap<>();  // Track variable usage per file

        try {
            CompilationUnit cu = StaticJavaParser.parse(javaFile);
            extractTypes(cu, data.get(fileKey), methodUsageCount);  // ✅ Pass methodUsageCount
            extractMethods(cu, data.get(fileKey), methodUsageCount);  // ✅ Pass methodUsageCount
            extractVariables(cu, data.get(fileKey), variableUsageCount);  // ✅ Pass variableUsageCount
            extractStringLiterals(cu, data.get(fileKey));
            extractCharLiterals(cu, data.get(fileKey));
            extractIntLiterals(cu, data.get(fileKey));

            // Process referenced classes from this file
            cu.findAll(NameExpr.class).forEach(expr -> {
                String referencedClass = expr.getNameAsString();
                if (parsedFiles.containsKey(referencedClass)) {
                    extractIdentifiersFromCU(parsedFiles.get(referencedClass), data, fileKey, methodUsageCount, variableUsageCount);  // ✅ Pass both counters
                }
            });

        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    private static void extractIdentifiersFromCU(CompilationUnit cu,
                                                 Map<String, Map<String, List<Map<String, Object>>>> data,
                                                 String fileKey,
                                                 Map<String, Integer> methodUsageCount,
                                                 Map<String, Integer> variableUsageCount) {  // ✅ Pass variableUsageCount
        extractTypes(cu, data.get(fileKey), methodUsageCount);  // ✅ Pass methodUsageCount
        extractMethods(cu, data.get(fileKey), methodUsageCount);  // ✅ Pass methodUsageCount
        extractVariables(cu, data.get(fileKey), variableUsageCount);  // ✅ Pass variableUsageCount
        extractStringLiterals(cu, data.get(fileKey));
        extractCharLiterals(cu, data.get(fileKey));
        extractIntLiterals(cu, data.get(fileKey));
    }




    private static String getClassName(CompilationUnit cu) {
        return cu.findFirst(ClassOrInterfaceDeclaration.class)
                .map(ClassOrInterfaceDeclaration::getNameAsString)
                .orElse(null);
    }


    private static void extractMethods(CompilationUnit cu, Map<String, List<Map<String, Object>>> data, Map<String, Integer> methodUsageCount) {
        Map<String, Map<String, Object>> uniqueMethodEntries = new HashMap<>(); // Track unique methods

        // Count method calls in the given compilation unit
        cu.findAll(MethodCallExpr.class).forEach(call -> {
            String methodName = call.getNameAsString();
            methodUsageCount.put(methodName, methodUsageCount.getOrDefault(methodName, 0) + 1);
        });

        // Extract method details while avoiding duplicates
        cu.findAll(MethodDeclaration.class).forEach(method -> {
            String qualifier = getEnclosingClass(method);
            String methodName = method.getNameAsString();
            int count = methodUsageCount.getOrDefault(methodName, 1);
            String modifier = method.getModifiers().stream()
                    .map(m -> m.toString().trim())
                    .collect(Collectors.joining(" "));

            // Construct method key (excluding `cnt`)
            String uniqueKey = qualifier + "|" + methodName + "|" + modifier + "|" + method.getType().toString() + "|" + method.getParameters().toString();

            // Check if a similar method entry exists
            if (uniqueMethodEntries.containsKey(uniqueKey)) {
                // Merge count if duplicate exists
                Map<String, Object> existingDetails = uniqueMethodEntries.get(uniqueKey);
                existingDetails.put("cnt", (int) existingDetails.get("cnt") + count);
            } else {
                // Otherwise, add a new entry
                Map<String, Object> details = new LinkedHashMap<>();
                details.put("qualifier", qualifier);
                details.put("modifier", modifier + " ");
                details.put("cnt", count);
                details.put("dtype", method.getType().toString());
                details.put("params", method.getParameters().stream()
                        .map(p -> p.getType().toString())
                        .toArray());
                details.put("itype", "METHOD");

                uniqueMethodEntries.put(uniqueKey, details);
            }
        });

        // Store unique method entries in data (Corrected type handling)
        for (Map.Entry<String, Map<String, Object>> entry : uniqueMethodEntries.entrySet()) {
            String methodName = entry.getKey().split("\\|")[1]; // Extract method name from key

            // Get the method details correctly
            Map<String, Object> methodDetails = entry.getValue();

            // Add the correctly casted map to the list
            data.computeIfAbsent(methodName, k -> new ArrayList<>()).add(methodDetails);
        }
    }





    private static void assignMethodToHierarchy(String className, String methodName,
                                                Map<String, List<Map<String, Object>>> data,
                                                Map<String, Integer> methodUsageCount) {
        Queue<String> queue = new LinkedList<>();
        Set<String> visited = new HashSet<>();
        queue.add(className);

        while (!queue.isEmpty()) {
            String currentClass = queue.poll();
            if (visited.contains(currentClass)) continue; // Avoid duplicate processing
            visited.add(currentClass);

            // Check if the current class has the method declared or defined
            if (!parsedFiles.containsKey(currentClass)) continue;
            CompilationUnit cu = parsedFiles.get(currentClass);

            // Find method declaration or definition in the current class
            Optional<MethodDeclaration> methodOpt = cu.findAll(MethodDeclaration.class)
                    .stream()
                    .filter(m -> m.getNameAsString().equals(methodName))
                    .findFirst();

            if (methodOpt.isPresent()) {
                MethodDeclaration method = methodOpt.get();

                // Retrieve or create method entry
                List<Map<String, Object>> methodList = data.computeIfAbsent(methodName, k -> new ArrayList<>());

                // Convert method properties into a details map
                String modifier = method.getModifiers().stream()
                        .map(m -> m.toString().trim())
                        .collect(Collectors.joining(" "));

                int count = methodUsageCount.getOrDefault(methodName, 1); // Get usage count

                Map<String, Object> methodDetails = new LinkedHashMap<>();
                methodDetails.put("qualifier", currentClass);
                methodDetails.put("modifier", modifier + " ");
                methodDetails.put("cnt", count); // Now correctly represents usage count
                methodDetails.put("dtype", method.getType().toString());
                methodDetails.put("params", method.getParameters().stream()
                        .map(p -> p.getType().toString())
                        .toArray());
                methodDetails.put("itype", "METHOD");

                // Avoid duplicate method entries
                Gson gson = new Gson();
                String jsonDetails = gson.toJson(methodDetails);

                Set<String> uniqueEntries = methodList.stream()
                        .map(gson::toJson)
                        .collect(Collectors.toSet());

                if (!uniqueEntries.contains(jsonDetails)) { // Only add if unique
                    methodList.add(methodDetails);
                }
            }

            // Add all parent classes/interfaces to the queue to track declared methods
            if (classHierarchy.containsKey(currentClass)) {
                queue.addAll(classHierarchy.get(currentClass));
            }
        }
    }


    private static void extractVariables(CompilationUnit cu, Map<String, List<Map<String, Object>>> data, Map<String, Integer> variableUsageCount) {
        Map<String, Map<String, Object>> uniqueVariableEntries = new HashMap<>(); // Track unique variables
        Set<String> methodNames = new HashSet<>(); // Track actual method names
        Set<String> classNames = new HashSet<>(); // Track actual class names

        // Collect method names first
        cu.findAll(MethodDeclaration.class).forEach(method -> methodNames.add(method.getNameAsString()));

        // Collect class names
        cu.findAll(ClassOrInterfaceDeclaration.class).forEach(cls -> classNames.add(cls.getNameAsString()));

        // Count how many times each variable is used (excluding method and class names)
        cu.findAll(NameExpr.class).forEach(expr -> {
            String varName = expr.getNameAsString();

            // ✅ Skip if the name is a known method or class
            if (methodNames.contains(varName) || classNames.contains(varName)) {
                return;
            }

            variableUsageCount.put(varName, variableUsageCount.getOrDefault(varName, 0) + 1);
        });

        // Extract variable details while avoiding duplicates
        cu.findAll(VariableDeclarator.class).forEach(var -> {
            String varName = var.getNameAsString();

            // ✅ Skip if the variable name conflicts with a method or class name
            if (methodNames.contains(varName) || classNames.contains(varName)) {
                return;
            }

            int count = variableUsageCount.getOrDefault(varName, 1);
            String dtype = var.getType().toString();
            String scope = getVariableScope(var);

            // Construct variable key (excluding `cnt`)
            String uniqueKey = scope + "|" + varName + "|" + dtype;

            if (uniqueVariableEntries.containsKey(uniqueKey)) {
                Map<String, Object> existingDetails = uniqueVariableEntries.get(uniqueKey);
                existingDetails.put("cnt", (int) existingDetails.get("cnt") + count);
            } else {
                Map<String, Object> details = new LinkedHashMap<>();
                details.put("qualifier", scope);
                details.put("cnt", count);
                details.put("dtype", dtype);
                details.put("itype", "VAR");

                uniqueVariableEntries.put(uniqueKey, details);
            }
        });

        for (Map.Entry<String, Map<String, Object>> entry : uniqueVariableEntries.entrySet()) {
            String varName = entry.getKey().split("\\|")[1]; // Extract variable name from key
            Map<String, Object> variableDetails = entry.getValue();
            data.computeIfAbsent(varName, k -> new ArrayList<>()).add(variableDetails);
        }
    }



    private static String getVariableScope(VariableDeclarator var) {
        Node parent = var;
        while (parent != null) {
            if (parent instanceof ClassOrInterfaceDeclaration) {
                return ((ClassOrInterfaceDeclaration) parent).getNameAsString(); // Class name as scope
            } else if (parent instanceof MethodDeclaration) {
                return ((MethodDeclaration) parent).getNameAsString(); // Method name as scope
            }
            parent = parent.getParentNode().orElse(null);
        }
        return "Unknown"; // Fallback if neither class nor method is found
    }


    private static void extractTypes(CompilationUnit cu, Map<String, List<Map<String, Object>>> data, Map<String, Integer> methodUsageCount) {
        Map<String, Integer> typeUsageCount = new HashMap<>();

        // Count class/interface references
        cu.findAll(NameExpr.class).forEach(expr -> {
            String typeName = expr.getNameAsString();
            typeUsageCount.put(typeName, typeUsageCount.getOrDefault(typeName, 0) + 1);
        });

        Gson gson = new Gson(); // Use Gson for duplicate checking

        cu.findAll(ClassOrInterfaceDeclaration.class).forEach(type -> {
            String typeName = type.getNameAsString();
            int count = typeUsageCount.getOrDefault(typeName, 1);

            // Extract superclass and implemented interfaces
            List<String> supers = new ArrayList<>();
            type.getExtendedTypes().forEach(extType -> supers.add(extType.getNameAsString()));
            type.getImplementedTypes().forEach(implType -> supers.add(implType.getNameAsString()));

            // Store in classHierarchy (child -> list of superclasses/interfaces)
            classHierarchy.put(typeName, supers);

            // Extract constructor parameter types as a list of lists
            List<List<String>> constructors = type.getConstructors().stream()
                    .map(constructor -> constructor.getParameters().stream()
                            .map(param -> param.getType().toString()) // Get parameter types
                            .collect(Collectors.toList()))
                    .collect(Collectors.toList());

            // Extract own fields
            Set<String> ownFields = type.getFields().stream()
                    .flatMap(field -> field.getVariables().stream().map(NodeWithSimpleName::getNameAsString))
                    .collect(Collectors.toSet());

            // Extract own methods
            Set<String> ownMethods = type.getMethods().stream()
                    .map(MethodDeclaration::getNameAsString)
                    .collect(Collectors.toSet());

            // Create a new map with identifier details
            Map<String, Object> details = new LinkedHashMap<>();
            details.put("methods", ownMethods.toArray());
            details.put("scope", typeName);
            details.put("cnt", count);
            details.put("supers", supers.toArray());
            details.put("fields", ownFields.toArray());
            details.put("constructors", constructors);
            details.put("itype", "TYPE");

            // Convert map to JSON string for proper duplicate checking
            String jsonDetails = gson.toJson(details);

            // Ensure no duplicate entries using a Set<String> for JSON comparison
            List<Map<String, Object>> existingEntries = data.computeIfAbsent(typeName, k -> new ArrayList<>());
            Set<String> uniqueEntries = existingEntries.stream()
                    .map(gson::toJson)
                    .collect(Collectors.toSet());

            if (!uniqueEntries.contains(jsonDetails)) { // Only add if unique
                existingEntries.add(details);
            }

            // 🔹 Assign each method to both its class & all base classes/interfaces
            for (String method : ownMethods) {
                assignMethodToHierarchy(typeName, method, data, methodUsageCount);  // ✅ Pass methodUsageCount
            }

            // 🔹 Assign each field to both its class & all base classes/interfaces
            for (String field : ownFields) {
                assignFieldToHierarchy(typeName, field, data);
            }
        });
    }


    private static void assignFieldToHierarchy(String className, String fieldName, Map<String, List<Map<String, Object>>> data) {
        Queue<String> queue = new LinkedList<>();
        Set<String> visited = new HashSet<>();
        queue.add(className);

        while (!queue.isEmpty()) {
            String currentClass = queue.poll();
            if (visited.contains(currentClass)) continue; // Avoid duplicate processing
            visited.add(currentClass);

            // Check if the current class has this field declared
            if (!parsedFiles.containsKey(currentClass)) continue;
            CompilationUnit cu = parsedFiles.get(currentClass);

            Optional<FieldDeclaration> fieldOpt = cu.findAll(FieldDeclaration.class)
                    .stream()
                    .flatMap(field -> field.getVariables().stream())
                    .filter(var -> var.getNameAsString().equals(fieldName))
                    .map(var -> (FieldDeclaration) var.getParentNode().orElse(null))
                    .findFirst();

            if (fieldOpt.isPresent()) {
                FieldDeclaration field = fieldOpt.get();

                // Retrieve or create field entry
                List<Map<String, Object>> fieldList = data.computeIfAbsent(fieldName, k -> new ArrayList<>());

                // Convert field properties into a details map
                String dtype = field.getElementType().toString();
                String modifier = field.getModifiers().stream()
                        .map(m -> m.toString().trim())
                        .collect(Collectors.joining(" "));

                Map<String, Object> fieldDetails = new LinkedHashMap<>();
                fieldDetails.put("qualifier", currentClass);
                fieldDetails.put("modifier", modifier + " ");
                fieldDetails.put("cnt", 1);
                fieldDetails.put("dtype", dtype);
                fieldDetails.put("itype", "VAR");

                // Avoid duplicate field entries
                Gson gson = new Gson();
                String jsonDetails = gson.toJson(fieldDetails);

                Set<String> uniqueEntries = fieldList.stream()
                        .map(gson::toJson)
                        .collect(Collectors.toSet());

                if (!uniqueEntries.contains(jsonDetails)) { // Only add if unique
                    fieldList.add(fieldDetails);
                }
            }

            // Add all parent classes/interfaces to the queue to track inherited fields
            if (classHierarchy.containsKey(currentClass)) {
                queue.addAll(classHierarchy.get(currentClass));
            }
        }
    }




    private static void extractStringLiterals(CompilationUnit cu, Map<String, List<Map<String, Object>>> data) {
        Map<String, Integer> stringUsageCount = new HashMap<>();

        cu.findAll(StringLiteralExpr.class).forEach(str -> {
            String value = str.getValue();
            stringUsageCount.put(value, stringUsageCount.getOrDefault(value, 0) + 1);
        });

        Gson gson = new Gson(); // Use Gson to serialize objects for duplicate checking

        stringUsageCount.forEach((value, count) -> {
            Map<String, Object> details = new LinkedHashMap<>();
            details.put("cnt", count);
            details.put("itype", "STRING");

            String jsonDetails = gson.toJson(details);

            List<Map<String, Object>> existingEntries = data.computeIfAbsent("\"" + value + "\"", k -> new ArrayList<>());
            Set<String> uniqueEntries = existingEntries.stream()
                    .map(gson::toJson)
                    .collect(Collectors.toSet());

            if (!uniqueEntries.contains(jsonDetails)) { // Only add if unique
                existingEntries.add(details);
            }
        });
    }



    private static void extractCharLiterals(CompilationUnit cu, Map<String, List<Map<String, Object>>> data) {
        Map<String, Integer> charUsageCount = new HashMap<>();

        cu.findAll(CharLiteralExpr.class).forEach(ch -> {
            String value = ch.getValue();
            charUsageCount.put(value, charUsageCount.getOrDefault(value, 0) + 1);
        });

        Gson gson = new Gson(); // Use Gson to serialize objects for duplicate checking

        charUsageCount.forEach((value, count) -> {
            Map<String, Object> details = new LinkedHashMap<>();
            details.put("cnt", count);
            details.put("itype", "CHAR");

            String jsonDetails = gson.toJson(details);

            List<Map<String, Object>> existingEntries = data.computeIfAbsent("'" + value + "'", k -> new ArrayList<>());
            Set<String> uniqueEntries = existingEntries.stream()
                    .map(gson::toJson)
                    .collect(Collectors.toSet());

            if (!uniqueEntries.contains(jsonDetails)) { // Only add if unique
                existingEntries.add(details);
            }
        });
    }


    private static void extractIntLiterals(CompilationUnit cu, Map<String, List<Map<String, Object>>> data) {
        Map<String, Integer> intUsageCount = new HashMap<>();

        cu.findAll(IntegerLiteralExpr.class).forEach(num -> {
            String value = num.getValue();
            intUsageCount.put(value, intUsageCount.getOrDefault(value, 0) + 1);
        });

        Gson gson = new Gson(); // Use Gson to serialize objects for duplicate checking

        intUsageCount.forEach((value, count) -> {
            Map<String, Object> details = new LinkedHashMap<>();
            details.put("cnt", count);
            details.put("itype", "INT");

            String jsonDetails = gson.toJson(details);

            List<Map<String, Object>> existingEntries = data.computeIfAbsent(value, k -> new ArrayList<>());
            Set<String> uniqueEntries = existingEntries.stream()
                    .map(gson::toJson)
                    .collect(Collectors.toSet());

            if (!uniqueEntries.contains(jsonDetails)) { // Only add if unique
                existingEntries.add(details);
            }
        });
    }


    private static String getEnclosingClass(Node node) {
        while (node != null) {
            if (node instanceof ClassOrInterfaceDeclaration) {
                return ((ClassOrInterfaceDeclaration) node).getNameAsString();
            }
            node = node.getParentNode().orElse(null); // Properly handle optional parent nodes
        }
        return "Unknown"; // Default if no class is found
    }
}
